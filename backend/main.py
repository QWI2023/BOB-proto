"""QAPIShield FastAPI Application - Zero Trust API Security & Third-Party Risk Management"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import json
from typing import List
from datetime import datetime
import pandas as pd
import os
import asyncio
from passlib.context import CryptContext
from pathlib import Path

# Import your modules
from . import models, schemas
from .database import get_db, engine
from .auth import authenticate_user, create_access_token, get_current_user
from .crypto.falcon import FalconCrypto
from .risk.engine import RiskEngine
from .anomaly.detector import AnomalyDetector
from .shadow.detector import ShadowAPIDetector
from .healing.engine import HealingEngine
from .config import settings
from .utils.logging import get_logger

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QAPIShield",
    description="Zero Trust API Security & Third-Party Risk Management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# FRONTEND MOUNTS
# -------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # proto directory

server_frontend = os.getenv("SERVER_FRONTEND", str(BASE_DIR / "frontend" / "server" / "dist"))
client_frontend = os.getenv("CLIENT_FRONTEND", str(BASE_DIR / "frontend" / "client" / "dist"))

# Mount static builds with html=True for SPA support
if os.path.exists(client_frontend):
    app.mount("/client", StaticFiles(directory=client_frontend, html=True), name="client")

if os.path.exists(server_frontend):
    app.mount("/server", StaticFiles(directory=server_frontend, html=True), name="server")

# -------------------
# Initialize components
# -------------------
logger = get_logger(__name__)
falcon_crypto = FalconCrypto()
risk_engine = RiskEngine()
anomaly_detector = AnomalyDetector()
shadow_detector = ShadowAPIDetector()
healing_engine = HealingEngine()

# -------------------
# DATASET INTEGRATION
# -------------------
train_df = None
test_df = None

@app.on_event("startup")
def load_datasets():
    global train_df, test_df
    dataset_path = os.getenv("QAPI_DATASETS", str(BASE_DIR / "datasets"))
    train_file = os.path.join(dataset_path, "main_training_dataset.csv")
    test_file = os.path.join(dataset_path, "main_testing_dataset.csv")

    if os.path.exists(train_file):
        train_df = pd.read_csv(train_file)
        logger.info(f"Training dataset loaded: {len(train_df)} rows")
    else:
        logger.warning("Training dataset not found!")

    if os.path.exists(test_file):
        test_df = pd.read_csv(test_file)
        logger.info(f"Testing dataset loaded: {len(test_df)} rows")
    else:
        logger.warning("Testing dataset not found!")

@app.get("/api/data/latest")
async def get_latest_data(n: int = 10):
    if test_df is None:
        raise HTTPException(status_code=500, detail="Testing dataset not loaded")
    return test_df.tail(n).to_dict(orient="records")

@app.get("/api/data/stats")
async def get_data_stats():
    if train_df is None or test_df is None:
        raise HTTPException(status_code=500, detail="Datasets not loaded")
    return {
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "columns": list(test_df.columns),
        "sample": test_df.head(5).to_dict(orient="records")
    }

@app.websocket("/api/data/stream")
async def stream_data(websocket: WebSocket):
    if test_df is None:
        await websocket.close(code=1011)
        return

    await websocket.accept()
    try:
        for _, row in test_df.iterrows():
            await websocket.send_json(row.to_dict())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    finally:
        await websocket.close()

# -------------------
# WEBSOCKET CONNECTIONS
# -------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# -------------------
# AUTHENTICATION
# -------------------
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/api/auth/login", response_model=schemas.LoginResponse)
async def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info=schemas.UserInfo(
            username=user.username,
            role=user.role,
            full_name=user.full_name,
            permissions=get_role_permissions(user.role)
        )
    )

def get_role_permissions(role: str) -> List[str]:
    permissions_map = {
        "admin": ["view_all", "manage_policies", "export_logs", "manage_users", "override_healing"],
        "vendor": ["view_own_requests", "view_risk_scores"],
        "employee": ["view_requests", "view_anomalies", "view_healing"],
        "external": ["view_limited"]
    }
    return permissions_map.get(role, [])

# -------------------
# DASHBOARD ENDPOINTS
# -------------------

@app.get("/api/dashboard/overview")
async def get_overview(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard overview KPIs"""
    # Calculate KPIs based on user role
    if current_user.role == "admin":
        total_requests = db.query(models.APIRequest).count()
        anomalies = db.query(models.AnomalyLog).filter(models.AnomalyLog.is_anomaly == True).count()
        active_vendors = db.query(models.Vendor).filter(models.Vendor.is_active == True).count()
        shadow_apis = db.query(models.ShadowAPI).count()
    elif current_user.role == "vendor":
        total_requests = db.query(models.APIRequest).filter(models.APIRequest.vendor_id == current_user.vendor_id).count()
        anomalies = db.query(models.AnomalyLog).join(models.APIRequest).filter(
            models.APIRequest.vendor_id == current_user.vendor_id,
            models.AnomalyLog.is_anomaly == True
        ).count()
        active_vendors = 1 if current_user.vendor_id else 0
        shadow_apis = 0
    else:
        total_requests = db.query(models.APIRequest).count()
        anomalies = db.query(models.AnomalyLog).filter(models.AnomalyLog.is_anomaly == True).count()
        active_vendors = db.query(models.Vendor).filter(models.Vendor.is_active == True).count()
        shadow_apis = db.query(models.ShadowAPI).count() if current_user.role == "employee" else 0
    
    avg_risk = db.query(models.func.avg(models.APIRequest.risk_score)).scalar() or 0
    
    return {
        "total_requests": total_requests,
        "anomalies_detected": anomalies,
        "average_risk_score": round(avg_risk, 1),
        "active_vendors": active_vendors,
        "shadow_apis_detected": shadow_apis,
        "system_health": "healthy"
    }

@app.get("/api/dashboard/requests")
async def get_api_requests(
    limit: int = 50,
    offset: int = 0,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get API requests with role-based filtering"""
    query = db.query(models.APIRequest)
    
    # Apply role-based filtering
    if current_user.role == "vendor":
        query = query.filter(models.APIRequest.vendor_id == current_user.vendor_id)
    elif current_user.role == "external":
        # External users see very limited data
        query = query.filter(models.APIRequest.risk_score < 30)
    
    requests = query.order_by(models.APIRequest.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "requests": [
            {
                "id": req.id,
                "timestamp": req.timestamp.isoformat(),
                "endpoint": req.endpoint,
                "method": req.method,
                "vendor_id": req.vendor_id,
                "crypto_valid": req.crypto_valid,
                "risk_score": req.risk_score,
                "mitigation_status": req.mitigation_status,
                "response_time": req.response_time
            }
            for req in requests
        ]
    }

@app.get("/api/dashboard/anomalies")
async def get_anomalies(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get anomaly detection results"""
    if current_user.role == "external":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(models.AnomalyLog).filter(models.AnomalyLog.is_anomaly == True)
    
    if current_user.role == "vendor":
        query = query.join(models.APIRequest).filter(models.APIRequest.vendor_id == current_user.vendor_id)
    
    anomalies = query.order_by(models.AnomalyLog.timestamp.desc()).limit(100).all()
    
    return {
        "anomalies": [
            {
                "id": anomaly.id,
                "timestamp": anomaly.timestamp.isoformat(),
                "request_id": anomaly.request_id,
                "anomaly_type": anomaly.anomaly_type,
                "confidence": anomaly.confidence,
                "details": anomaly.details
            }
            for anomaly in anomalies
        ]
    }

@app.get("/api/dashboard/shadow-apis")
async def get_shadow_apis(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get shadow API detection results"""
    if current_user.role not in ["admin", "employee"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    shadow_apis = db.query(models.ShadowAPI).order_by(models.ShadowAPI.discovered_at.desc()).limit(50).all()
    
    return {
        "shadow_apis": [
            {
                "id": shadow.id,
                "endpoint": shadow.endpoint,
                "method": shadow.method,
                "discovered_at": shadow.discovered_at.isoformat(),
                "risk_level": shadow.risk_level,
                "usage_count": shadow.usage_count,
                "last_seen": shadow.last_seen.isoformat()
            }
            for shadow in shadow_apis
        ]
    }

@app.get("/api/dashboard/healing")
async def get_healing_actions(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get self-healing actions and logs"""
    if current_user.role == "external":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(models.HealingLog)
    
    if current_user.role == "vendor":
        query = query.join(models.APIRequest).filter(models.APIRequest.vendor_id == current_user.vendor_id)
    
    healing_logs = query.order_by(models.HealingLog.timestamp.desc()).limit(100).all()
    
    return {
        "healing_actions": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "request_id": log.request_id,
                "action": log.action,
                "reason": log.reason,
                "auto_applied": log.auto_applied,
                "effectiveness": log.effectiveness
            }
            for log in healing_logs
        ]
    }

@app.post("/api/healing/override")
async def override_healing_action(
    override: schemas.HealingOverride,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manual override of healing action (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Apply manual override
    healing_log = models.HealingLog(
        request_id=override.request_id,
        action=override.action,
        reason=f"Manual override by {current_user.username}: {override.reason}",
        auto_applied=False,
        timestamp=datetime.utcnow()
    )
    
    db.add(healing_log)
    db.commit()
    
    # Broadcast update
    await manager.broadcast({
        "type": "healing_override",
        "data": {
            "request_id": override.request_id,
            "action": override.action,
            "user": current_user.username
        }
    })
    
    return {"status": "success", "message": "Healing action overridden"}

@app.get("/api/audit/logs")
async def get_audit_logs(
    format: str = "json",
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export audit logs (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all audit data
    requests = db.query(models.APIRequest).all()
    anomalies = db.query(models.AnomalyLog).all()
    healing_logs = db.query(models.HealingLog).all()
    
    if format == "csv":
        # Create CSV export
        data = []
        for req in requests:
            data.append({
                "timestamp": req.timestamp.isoformat(),
                "type": "api_request",
                "endpoint": req.endpoint,
                "vendor_id": req.vendor_id,
                "risk_score": req.risk_score,
                "crypto_valid": req.crypto_valid,
                "mitigation_status": req.mitigation_status
            })
        
        df = pd.DataFrame(data)
        csv_path = f"/tmp/qapishield_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False)
        return FileResponse(csv_path, media_type="text/csv", filename="qapishield_audit.csv")
    
    else:
        # JSON export
        return {
            "export_timestamp": datetime.utcnow().isoformat(),
            "requests": len(requests),
            "anomalies": len(anomalies),
            "healing_actions": len(healing_logs),
            "data": {
                "requests": [
                    {
                        "id": req.id,
                        "timestamp": req.timestamp.isoformat(),
                        "endpoint": req.endpoint,
                        "vendor_id": req.vendor_id,
                        "risk_score": req.risk_score,
                        "crypto_valid": req.crypto_valid
                    }
                    for req in requests[-100:]  # Last 100 for size
                ]
            }
        }

@app.post("/api/requests/simulate")
async def simulate_api_request(
    request_data: schemas.APIRequestSimulation,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Simulate an API request for testing"""
    crypto_valid = await falcon_crypto.verify_signature(
        request_data.payload,
        request_data.signature,
        request_data.vendor_id
    )
    risk_score = risk_engine.calculate_risk(
        crypto_valid=crypto_valid,
        vendor_reputation=request_data.vendor_reputation,
        endpoint_sensitivity=request_data.endpoint_sensitivity,
        request_frequency=request_data.request_frequency,
        geo_location=request_data.geo_location
    )
    anomaly_result = await anomaly_detector.detect_anomaly(request_data.dict())
    shadow_result = await shadow_detector.check_endpoint(request_data.endpoint, request_data.method)
    healing_action = healing_engine.decide_action(
        risk_score=risk_score,
        anomaly_detected=anomaly_result["is_anomaly"],
        crypto_valid=crypto_valid
    )
    api_request = models.APIRequest(
        endpoint=request_data.endpoint,
        method=request_data.method,
        vendor_id=request_data.vendor_id,
        crypto_valid=crypto_valid,
        risk_score=risk_score,
        mitigation_status=healing_action["action"],
        response_time=request_data.response_time or 150,
        timestamp=datetime.utcnow()
    )
    db.add(api_request)
    db.commit()
    db.refresh(api_request)
    # store anomaly/healing logs...
    return {
        "request_id": api_request.id,
        "crypto_valid": crypto_valid,
        "risk_score": risk_score,
        "anomaly_result": anomaly_result,
        "shadow_api": shadow_result,
        "healing_action": healing_action,
        "timestamp": api_request.timestamp.isoformat()
    }

async def broadcast_update(message: dict):
    await manager.broadcast(message)

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# -------------------
# FRONTEND ROUTING
# -------------------
@app.get("/")
async def root_redirect():
    """Redirect root to client frontend"""
    return FileResponse(os.path.join(client_frontend, "index.html"))

@app.get("/client")
async def serve_client():
    """Serve client frontend"""
    return FileResponse(os.path.join(client_frontend, "index.html"))

@app.get("/server")
async def serve_server():
    """Serve server frontend"""
    return FileResponse(os.path.join(server_frontend, "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/debug/requests")
async def debug_requests(db: Session = Depends(get_db)):
    """Quick debug endpoint to fetch last 5 requests without auth"""
    requests = db.query(models.APIRequest).order_by(models.APIRequest.timestamp.desc()).limit(5).all()
    return [
        {
            "id": req.id,
            "timestamp": req.timestamp.isoformat(),
            "endpoint": req.endpoint,
            "method": req.method,
            "vendor_id": req.vendor_id,
            "risk_score": req.risk_score,
            "mitigation_status": req.mitigation_status
        }
        for req in requests
    ]
# -------------------
# UVICORN ENTRY
# -------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)