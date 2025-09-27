                               QAPIShield – Zero Trust API Security & Risk Management Prototype

**Overview**

QAPIShield is a Zero-Trust API Security framework designed to secure financial and healthcare APIs against insider threats, API misuse, and third-party risks.
This prototype was developed for a hackathon and demonstrates real-time API request validation, hybrid anomaly detection, risk scoring, and self-healing.

The system enforces multi-layered security checks:
- Post-Quantum Cryptography (Falcon-512) for signature verification.
- ABAC (Attribute-Based Access Control) for fine-grained role + attribute policies.
- Shadow API Detection to block undocumented endpoints.
- Hybrid Anomaly Detection using ML-based risk scoring.
- Self-Healing Engine to adaptively challenge/deny repeated attack attempts.
- Monitoring & Reporting Dashboard for admins and vendors.

**Prototype Modules**
1. Cryptographic Module
- Falcon-512 signature validation (simulated if PQC libs unavailable).
- Detects tampered or invalid API requests.

2. Shadow API Detection Module
- Identifies undocumented/hidden API calls.
- Blocks unauthorized endpoints automatically.

3. ABAC Module
- Enforces attribute-based policies.
- Examples:
- Employee can only approve ≤ ₹50,000 transactions.
- Auditor can only view logs/reports from HQ.

4. Hybrid Anomaly Detection Module
- Extracts request features: frequency, vendor reputation, transaction size, time.
- Detects deviations from baseline using hybrid ML model.

5. Risk Scoring Module
- Aggregates outputs from crypto, ABAC, anomaly, shadow detection.
- Normalized 0–100 score:
    a. <30 → Permit
    b. 30–70 → Challenge (step-up auth)
    c. >70 → Deny

6. Self-Healing Module
- Adapts to repeated threats (invalid signatures, shadow API abuse).
- Escalates from deny → challenge → block.

7. Monitoring & Reporting Module
- Real-time dashboards for vendors/admins.
- CSV/JSON log exports for compliance.
- WebSocket updates for live monitoring.

**System Architecture**

Frontend:
- /client → API Request Simulation page.
- /server → Monitoring Dashboard.

Backend:
- FastAPI app with /api/* endpoints.
- SQLite/Postgres storage for logs.

**Setup Instructions**

1. Clone repo:
- git clone https://github.com/QWI2023/BOB-proto.git
- cd BOB-proto

2. Backend Setup
- python -m venv venv
- venv\Scripts\activate    # On Windows
- pip install -r requirements.txt
  
- Run FastAPI server

  uvicorn backend.main:app --reload --port 8000

3. Frontend Setup
- cd frontend/client
- npm install
- npm run build

- cd ../server
- npm install
- npm run build

4. Access Frontend

- Client Side: http://127.0.0.1:8000/client
- Server side Dashboard: http://127.0.0.1:8000/server

**Tech Stack**

- Backend: FastAPI, SQLAlchemy, Pydantic, scikit-learn, Torch.
- Frontend: React (Vite), WebSockets.
- Database: SQLite / Postgres.
- Crypto: Falcon-512

**How to Demo**

- Open /client → login as a user, send API requests.
- Requests flow through → Crypto → ABAC → Shadow API → Anomaly → Risk Scoring → Self-Healing.
- Open /server → monitor live risk scores, anomalies, shadow API attempts.
- Trigger invalid requests → see system adapt (deny → challenge → block).
- Export logs → CSV/JSON from Reports tab.

**Contributors**

Quantum Weave Intelligence Pvt Ltd.(QWI)

Email: projects@quantumweaveintelligence.com

GitHub repo: QWI2023
  
   
