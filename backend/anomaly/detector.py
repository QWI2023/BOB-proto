"""Anomaly Detection Module"""
import json
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AnomalyDetector:
    """Anomaly detection for API requests"""
    
    def __init__(self):
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            "request_frequency", "payload_size", "response_time",
            "hour_of_day", "day_of_week", "vendor_reputation"
        ]
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize anomaly detection models"""
        try:
            # Try to load pre-trained model
            model_path = "models/anomaly_detector.pkl"
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    model_data = pickle.load(f)
                    self.isolation_forest = model_data["model"]
                    self.scaler = model_data["scaler"]
                    self.is_trained = True
                    logger.info("Loaded pre-trained anomaly detection model")
            else:
                # Initialize with default parameters
                self.isolation_forest = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )
                logger.info("Initialized new anomaly detection model")
                
        except Exception as e:
            logger.error(f"Failed to initialize anomaly detector: {e}")
            self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    
    async def detect_anomaly(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in API request"""
        try:
            # Extract features
            features = self._extract_features(request_data)
            
            if not self.is_trained:
                # Use rule-based detection for untrained model
                return self._rule_based_detection(request_data, features)
            
            # ML-based detection
            features_scaled = self.scaler.transform([features])
            anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
            is_anomaly = self.isolation_forest.predict(features_scaled)[0] == -1
            
            # Convert score to confidence (0-1)
            confidence = min(1.0, abs(anomaly_score))
            
            result = {
                "is_anomaly": is_anomaly,
                "confidence": confidence,
                "type": "ml_based",
                "details": {
                    "anomaly_score": float(anomaly_score),
                    "features": dict(zip(self.feature_names, features)),
                    "threshold": -0.1
                }
            }
            
            logger.debug(f"ML anomaly detection: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {
                "is_anomaly": False,
                "confidence": 0.0,
                "type": "error",
                "details": {"error": str(e)}
            }
    
    def _extract_features(self, request_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from request data"""
        now = datetime.utcnow()
        
        features = [
            float(request_data.get("request_frequency", 1)),
            float(len(request_data.get("payload", ""))),
            float(request_data.get("response_time", 100)),
            float(now.hour),
            float(now.weekday()),
            float(request_data.get("vendor_reputation", 50.0))
        ]
        
        return features
    
    def _rule_based_detection(self, request_data: Dict[str, Any], features: List[float]) -> Dict[str, Any]:
        """Rule-based anomaly detection for untrained models"""
        anomalies = []
        confidence = 0.0
        
        # High frequency check
        if features[0] > 50:  # request_frequency
            anomalies.append("high_frequency")
            confidence += 0.3
        
        # Large payload check
        if features[1] > 10000:  # payload_size
            anomalies.append("large_payload")
            confidence += 0.2
        
        # Slow response check
        if features[2] > 5000:  # response_time
            anomalies.append("slow_response")
            confidence += 0.2
        
        # Off-hours check
        if features[3] < 6 or features[3] > 22:  # hour_of_day
            anomalies.append("off_hours")
            confidence += 0.1
        
        # Low vendor reputation
        if features[5] < 30:  # vendor_reputation
            anomalies.append("low_reputation")
            confidence += 0.4
        
        is_anomaly = len(anomalies) > 0 and confidence > 0.3
        
        return {
            "is_anomaly": is_anomaly,
            "confidence": min(1.0, confidence),
            "type": "rule_based",
            "details": {
                "triggered_rules": anomalies,
                "features": dict(zip(self.feature_names, features))
            }
        }
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the anomaly detection model"""
        try:
            if len(training_data) < 10:
                logger.warning("Insufficient training data for anomaly detection")
                return
            
            # Extract features from training data
            features_list = []
            for data in training_data:
                features = self._extract_features(data)
                features_list.append(features)
            
            features_array = np.array(features_list)
            
            # Fit scaler and model
            features_scaled = self.scaler.fit_transform(features_array)
            self.isolation_forest.fit(features_scaled)
            self.is_trained = True
            
            # Save model
            os.makedirs("models", exist_ok=True)
            model_data = {
                "model": self.isolation_forest,
                "scaler": self.scaler,
                "feature_names": self.feature_names
            }
            
            with open("models/anomaly_detector.pkl", "wb") as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Trained anomaly detection model with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the anomaly detection model"""
        return {
            "is_trained": self.is_trained,
            "model_type": "IsolationForest",
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "contamination": 0.1 if self.isolation_forest else None
        }
    
    def generate_synthetic_anomalies(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate synthetic anomalies for testing"""
        anomalies = []
        
        for i in range(count):
            anomaly = {
                "endpoint": f"/api/suspicious/endpoint_{i}",
                "method": "POST",
                "vendor_id": f"suspicious_vendor_{i}",
                "request_frequency": np.random.randint(100, 500),  # High frequency
                "payload": "x" * np.random.randint(5000, 20000),  # Large payload
                "response_time": np.random.randint(3000, 10000),  # Slow response
                "vendor_reputation": np.random.uniform(0, 20),  # Low reputation
                "timestamp": datetime.utcnow() - timedelta(minutes=np.random.randint(1, 60))
            }
            anomalies.append(anomaly)
        
        return anomalies