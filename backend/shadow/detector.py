"""Shadow API Detection Module"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ShadowAPIDetector:
    """Shadow API detection and monitoring"""
    
    def __init__(self):
        self.documented_apis = set()
        self.discovered_endpoints = defaultdict(dict)
        self.usage_patterns = defaultdict(list)
        self._load_documented_apis()
    
    def _load_documented_apis(self):
        """Load documented API endpoints"""
        # In production, this would load from API documentation/OpenAPI specs
        documented_endpoints = [
            "/api/auth/login",
            "/api/dashboard/overview",
            "/api/dashboard/requests",
            "/api/dashboard/anomalies",
            "/api/dashboard/healing",
            "/api/requests/simulate",
            "/api/audit/logs",
            "/health",
            "/ws/live"
        ]
        
        self.documented_apis = set(documented_endpoints)
        logger.info(f"Loaded {len(documented_endpoints)} documented API endpoints")
    
    async def check_endpoint(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Check if endpoint is a potential shadow API"""
        try:
            # Normalize endpoint (remove query parameters, IDs)
            normalized_endpoint = self._normalize_endpoint(endpoint)
            
            # Check if endpoint is documented
            is_documented = normalized_endpoint in self.documented_apis
            
            # Track usage
            self._track_usage(normalized_endpoint, method)
            
            # Determine risk level
            risk_level = self._assess_risk(normalized_endpoint, method, is_documented)
            
            result = {
                "endpoint": endpoint,
                "normalized_endpoint": normalized_endpoint,
                "method": method,
                "is_shadow_api": not is_documented,
                "risk_level": risk_level,
                "usage_count": len(self.usage_patterns[normalized_endpoint]),
                "first_seen": self.discovered_endpoints[normalized_endpoint].get("first_seen"),
                "patterns": self._analyze_patterns(normalized_endpoint)
            }
            
            # Store discovery if it's a new shadow API
            if not is_documented and normalized_endpoint not in self.discovered_endpoints:
                self.discovered_endpoints[normalized_endpoint] = {
                    "first_seen": datetime.utcnow(),
                    "method": method,
                    "risk_level": risk_level,
                    "usage_count": 1
                }
                logger.warning(f"Shadow API detected: {method} {normalized_endpoint}")
            
            return result
            
        except Exception as e:
            logger.error(f"Shadow API detection failed: {e}")
            return {
                "endpoint": endpoint,
                "is_shadow_api": False,
                "risk_level": "unknown",
                "error": str(e)
            }
    
    def _normalize_endpoint(self, endpoint: str) -> str:
        """Normalize endpoint by removing IDs and query parameters"""
        # Remove query parameters
        endpoint = endpoint.split('?')[0]
        
        # Replace numeric IDs with placeholder
        endpoint = re.sub(r'/\d+', '/{id}', endpoint)
        
        # Replace UUIDs with placeholder
        endpoint = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', endpoint)
        
        # Replace other common ID patterns
        endpoint = re.sub(r'/[a-zA-Z0-9_-]{20,}', '/{token}', endpoint)
        
        return endpoint
    
    def _track_usage(self, endpoint: str, method: str):
        """Track endpoint usage patterns"""
        usage_entry = {
            "timestamp": datetime.utcnow(),
            "method": method
        }
        
        self.usage_patterns[endpoint].append(usage_entry)
        
        # Keep only recent usage (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.usage_patterns[endpoint] = [
            entry for entry in self.usage_patterns[endpoint]
            if entry["timestamp"] > cutoff_time
        ]
    
    def _assess_risk(self, endpoint: str, method: str, is_documented: bool) -> str:
        """Assess risk level of endpoint"""
        if is_documented:
            return "none"
        
        risk_score = 0
        
        # High-risk patterns
        high_risk_patterns = [
            r'/admin/',
            r'/internal/',
            r'/debug/',
            r'/test/',
            r'/dev/',
            r'\.php$',
            r'\.asp$',
            r'/backup/',
            r'/config/',
            r'/private/'
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, endpoint, re.IGNORECASE):
                risk_score += 3
                break
        
        # Medium-risk patterns
        medium_risk_patterns = [
            r'/api/v\d+/',
            r'/legacy/',
            r'/old/',
            r'/temp/',
            r'/upload/',
            r'/download/'
        ]
        
        for pattern in medium_risk_patterns:
            if re.search(pattern, endpoint, re.IGNORECASE):
                risk_score += 2
                break
        
        # Method-based risk
        if method in ["DELETE", "PUT", "PATCH"]:
            risk_score += 1
        
        # Usage frequency risk
        usage_count = len(self.usage_patterns[endpoint])
        if usage_count > 100:
            risk_score += 2
        elif usage_count > 10:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 5:
            return "critical"
        elif risk_score >= 3:
            return "high"
        elif risk_score >= 1:
            return "medium"
        else:
            return "low"
    
    def _analyze_patterns(self, endpoint: str) -> Dict[str, Any]:
        """Analyze usage patterns for endpoint"""
        usage_list = self.usage_patterns[endpoint]
        
        if not usage_list:
            return {}
        
        # Calculate usage frequency
        now = datetime.utcnow()
        last_hour = sum(1 for entry in usage_list if (now - entry["timestamp"]).seconds < 3600)
        last_day = len(usage_list)
        
        # Method distribution
        methods = defaultdict(int)
        for entry in usage_list:
            methods[entry["method"]] += 1
        
        # Time pattern analysis
        hours = [entry["timestamp"].hour for entry in usage_list]
        peak_hour = max(set(hours), key=hours.count) if hours else 0
        
        return {
            "usage_last_hour": last_hour,
            "usage_last_day": last_day,
            "method_distribution": dict(methods),
            "peak_hour": peak_hour,
            "is_burst_pattern": last_hour > last_day * 0.5,
            "is_regular_pattern": len(set(hours)) < 6  # Used in less than 6 different hours
        }
    
    def get_shadow_apis(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get discovered shadow APIs"""
        shadow_apis = []
        
        for endpoint, info in self.discovered_endpoints.items():
            shadow_api = {
                "endpoint": endpoint,
                "method": info["method"],
                "first_seen": info["first_seen"].isoformat(),
                "risk_level": info["risk_level"],
                "usage_count": len(self.usage_patterns[endpoint]),
                "last_seen": max(
                    (entry["timestamp"] for entry in self.usage_patterns[endpoint]),
                    default=info["first_seen"]
                ).isoformat(),
                "patterns": self._analyze_patterns(endpoint)
            }
            shadow_apis.append(shadow_api)
        
        # Sort by risk level and usage count
        risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0}
        shadow_apis.sort(
            key=lambda x: (risk_order.get(x["risk_level"], 0), x["usage_count"]),
            reverse=True
        )
        
        return shadow_apis[:limit]
    
    def generate_synthetic_shadow_apis(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate synthetic shadow APIs for demo"""
        synthetic_apis = [
            {
                "endpoint": "/api/internal/admin/users",
                "method": "GET",
                "risk_level": "critical",
                "usage_count": 45,
                "discovered_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "endpoint": "/legacy/v1/payments/process",
                "method": "POST", 
                "risk_level": "high",
                "usage_count": 23,
                "discovered_at": datetime.utcnow() - timedelta(hours=6)
            },
            {
                "endpoint": "/debug/api/logs",
                "method": "GET",
                "risk_level": "high",
                "usage_count": 12,
                "discovered_at": datetime.utcnow() - timedelta(hours=12)
            },
            {
                "endpoint": "/api/v2/experimental/features",
                "method": "GET",
                "risk_level": "medium",
                "usage_count": 8,
                "discovered_at": datetime.utcnow() - timedelta(hours=18)
            },
            {
                "endpoint": "/temp/upload/files",
                "method": "POST",
                "risk_level": "medium",
                "usage_count": 5,
                "discovered_at": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        return synthetic_apis[:count]