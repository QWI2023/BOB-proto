"""Risk Scoring Engine"""
from typing import Dict, Any
from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class RiskEngine:
    """Risk scoring engine for API requests"""
    
    def __init__(self):
        self.weights = {
            "crypto": settings.crypto_weight,
            "vendor": settings.vendor_weight,
            "anomaly": settings.anomaly_weight,
            "frequency": settings.frequency_weight,
            "geo": settings.geo_weight
        }
    
    def calculate_risk(
        self,
        crypto_valid: bool,
        vendor_reputation: float,
        endpoint_sensitivity: str,
        request_frequency: int,
        geo_location: str,
        anomaly_score: float = 0.0
    ) -> float:
        """Calculate risk score (0-100)"""
        
        # Crypto risk component
        crypto_risk = 0.0 if crypto_valid else 1.0
        
        # Vendor reputation risk (invert reputation score)
        vendor_risk = max(0.0, (100 - vendor_reputation) / 100)
        
        # Endpoint sensitivity risk
        sensitivity_risk = self._get_sensitivity_risk(endpoint_sensitivity)
        
        # Request frequency risk
        frequency_risk = min(1.0, request_frequency / 100)  # Normalize to 0-1
        
        # Geographic risk (simplified)
        geo_risk = self._get_geo_risk(geo_location)
        
        # Weighted risk calculation
        weighted_risk = (
            self.weights["crypto"] * crypto_risk +
            self.weights["vendor"] * vendor_risk +
            self.weights["anomaly"] * anomaly_score +
            self.weights["frequency"] * frequency_risk +
            self.weights["geo"] * geo_risk
        )
        
        # Add sensitivity multiplier
        if endpoint_sensitivity == "high":
            weighted_risk *= 1.2
        elif endpoint_sensitivity == "critical":
            weighted_risk *= 1.5
        
        # Clamp to 0-100 range
        risk_score = max(0.0, min(100.0, weighted_risk * 100))
        
        logger.debug(f"Risk calculation: crypto={crypto_risk}, vendor={vendor_risk}, "
                    f"sensitivity={sensitivity_risk}, frequency={frequency_risk}, "
                    f"geo={geo_risk}, final={risk_score}")
        
        return round(risk_score, 1)
    
    def _get_sensitivity_risk(self, sensitivity: str) -> float:
        """Get risk multiplier based on endpoint sensitivity"""
        sensitivity_map = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.6,
            "critical": 0.9
        }
        return sensitivity_map.get(sensitivity.lower(), 0.3)
    
    def _get_geo_risk(self, geo_location: str) -> float:
        """Get risk score based on geographic location"""
        # Simplified geo risk (in production, this would use threat intelligence)
        high_risk_countries = ["XX", "YY", "ZZ"]  # Placeholder
        medium_risk_countries = ["AA", "BB", "CC"]
        
        if geo_location in high_risk_countries:
            return 0.8
        elif geo_location in medium_risk_countries:
            return 0.4
        else:
            return 0.1
    
    def get_risk_level(self, risk_score: float) -> str:
        """Get risk level category"""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        elif risk_score >= 20:
            return "low"
        else:
            return "minimal"
    
    def get_risk_breakdown(
        self,
        crypto_valid: bool,
        vendor_reputation: float,
        endpoint_sensitivity: str,
        request_frequency: int,
        geo_location: str,
        anomaly_score: float = 0.0
    ) -> Dict[str, Any]:
        """Get detailed risk breakdown"""
        
        crypto_risk = 0.0 if crypto_valid else 1.0
        vendor_risk = max(0.0, (100 - vendor_reputation) / 100)
        sensitivity_risk = self._get_sensitivity_risk(endpoint_sensitivity)
        frequency_risk = min(1.0, request_frequency / 100)
        geo_risk = self._get_geo_risk(geo_location)
        
        total_risk = self.calculate_risk(
            crypto_valid, vendor_reputation, endpoint_sensitivity,
            request_frequency, geo_location, anomaly_score
        )
        
        return {
            "total_score": total_risk,
            "level": self.get_risk_level(total_risk),
            "components": {
                "crypto_risk": round(crypto_risk * 100, 1),
                "vendor_risk": round(vendor_risk * 100, 1),
                "sensitivity_risk": round(sensitivity_risk * 100, 1),
                "frequency_risk": round(frequency_risk * 100, 1),
                "geo_risk": round(geo_risk * 100, 1),
                "anomaly_risk": round(anomaly_score * 100, 1)
            },
            "weights": self.weights
        }