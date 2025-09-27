"""Self-Healing Engine"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class HealingEngine:
    """Self-healing decision engine for API security"""
    
    def __init__(self):
        self.action_history = []
        self.effectiveness_scores = {
            "allow": 0.9,
            "challenge": 0.8,
            "block": 0.95,
            "delay": 0.7,
            "retrain": 0.6
        }
    
    def decide_action(
        self,
        risk_score: float,
        anomaly_detected: bool,
        crypto_valid: bool,
        vendor_reputation: float = 50.0,
        endpoint_sensitivity: str = "medium"
    ) -> Dict[str, Any]:
        """Decide healing action based on risk assessment"""
        
        try:
            # Initialize decision context
            context = {
                "risk_score": risk_score,
                "anomaly_detected": anomaly_detected,
                "crypto_valid": crypto_valid,
                "vendor_reputation": vendor_reputation,
                "endpoint_sensitivity": endpoint_sensitivity,
                "timestamp": datetime.utcnow()
            }
            
            # Apply decision logic
            action, reason, confidence = self._apply_decision_logic(context)
            
            # Calculate effectiveness prediction
            effectiveness = self._predict_effectiveness(action, context)
            
            # Record decision
            decision = {
                "action": action,
                "reason": reason,
                "confidence": confidence,
                "effectiveness": effectiveness,
                "context": context,
                "auto_applied": True
            }
            
            self._record_decision(decision)
            
            logger.info(f"Healing decision: {action} (confidence: {confidence:.2f}, "
                       f"effectiveness: {effectiveness:.2f}) - {reason}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Healing decision failed: {e}")
            return {
                "action": "allow",
                "reason": f"Error in healing engine: {str(e)}",
                "confidence": 0.1,
                "effectiveness": 0.5,
                "auto_applied": True
            }
    
    def _apply_decision_logic(self, context: Dict[str, Any]) -> tuple:
        """Apply decision logic and return action, reason, confidence"""
        
        risk_score = context["risk_score"]
        anomaly_detected = context["anomaly_detected"]
        crypto_valid = context["crypto_valid"]
        vendor_reputation = context["vendor_reputation"]
        endpoint_sensitivity = context["endpoint_sensitivity"]
        
        # Critical risk - immediate block
        if risk_score >= settings.high_risk_threshold:
            return "block", f"Critical risk score: {risk_score}/100", 0.95
        
        # Invalid crypto - block or challenge based on vendor reputation
        if not crypto_valid:
            if vendor_reputation < 30:
                return "block", "Invalid signature from low-reputation vendor", 0.9
            else:
                return "challenge", "Invalid signature requires additional verification", 0.8
        
        # Anomaly detected
        if anomaly_detected:
            if risk_score > 60:
                return "block", "Anomaly detected with high risk score", 0.85
            elif endpoint_sensitivity == "high":
                return "challenge", "Anomaly detected on sensitive endpoint", 0.8
            else:
                return "delay", "Anomaly detected, applying throttling", 0.7
        
        # High risk but not critical
        if risk_score >= settings.medium_risk_threshold:
            if endpoint_sensitivity == "high":
                return "challenge", f"High risk ({risk_score}) on sensitive endpoint", 0.75
            else:
                return "delay", f"High risk ({risk_score}), applying delay", 0.7
        
        # Low vendor reputation
        if vendor_reputation < 40:
            return "challenge", f"Low vendor reputation: {vendor_reputation}/100", 0.6
        
        # Sensitive endpoint with medium risk
        if endpoint_sensitivity == "high" and risk_score > 30:
            return "challenge", "Sensitive endpoint requires additional verification", 0.65
        
        # Default allow for low risk
        return "allow", f"Low risk score: {risk_score}/100", 0.9
    
    def _predict_effectiveness(self, action: str, context: Dict[str, Any]) -> float:
        """Predict effectiveness of healing action"""
        
        base_effectiveness = self.effectiveness_scores.get(action, 0.5)
        
        # Adjust based on context
        risk_score = context["risk_score"]
        
        # Higher risk scenarios benefit more from restrictive actions
        if action in ["block", "challenge"] and risk_score > 70:
            base_effectiveness += 0.1
        
        # Lower risk scenarios may not need restrictive actions
        if action in ["block", "challenge"] and risk_score < 30:
            base_effectiveness -= 0.2
        
        # Crypto validation affects effectiveness
        if not context["crypto_valid"] and action in ["block", "challenge"]:
            base_effectiveness += 0.05
        
        # Vendor reputation affects effectiveness
        vendor_reputation = context["vendor_reputation"]
        if vendor_reputation < 30 and action == "block":
            base_effectiveness += 0.1
        elif vendor_reputation > 80 and action == "allow":
            base_effectiveness += 0.05
        
        return max(0.0, min(1.0, base_effectiveness))
    
    def _record_decision(self, decision: Dict[str, Any]):
        """Record healing decision for learning"""
        self.action_history.append(decision)
        
        # Keep only recent history (last 1000 decisions)
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-500:]
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about healing actions"""
        if not self.action_history:
            return {
                "total_decisions": 0,
                "action_distribution": {},
                "average_confidence": 0.0,
                "average_effectiveness": 0.0
            }
        
        # Count actions
        action_counts = {}
        total_confidence = 0.0
        total_effectiveness = 0.0
        
        for decision in self.action_history:
            action = decision["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
            total_confidence += decision["confidence"]
            total_effectiveness += decision["effectiveness"]
        
        total_decisions = len(self.action_history)
        
        return {
            "total_decisions": total_decisions,
            "action_distribution": action_counts,
            "average_confidence": total_confidence / total_decisions,
            "average_effectiveness": total_effectiveness / total_decisions,
            "recent_decisions": self.action_history[-10:]  # Last 10 decisions
        }
    
    def override_action(
        self,
        request_id: int,
        new_action: str,
        reason: str,
        user: str
    ) -> Dict[str, Any]:
        """Manual override of healing action"""
        
        override_decision = {
            "action": new_action,
            "reason": f"Manual override by {user}: {reason}",
            "confidence": 1.0,  # Manual decisions have full confidence
            "effectiveness": self.effectiveness_scores.get(new_action, 0.5),
            "auto_applied": False,
            "override_user": user,
            "override_timestamp": datetime.utcnow(),
            "request_id": request_id
        }
        
        self._record_decision(override_decision)
        
        logger.info(f"Manual override by {user}: {new_action} for request {request_id}")
        
        return override_decision
    
    def get_recommended_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommended actions with confidence scores"""
        
        # Get primary recommendation
        primary_action, primary_reason, primary_confidence = self._apply_decision_logic(context)
        
        recommendations = [
            {
                "action": primary_action,
                "reason": primary_reason,
                "confidence": primary_confidence,
                "effectiveness": self._predict_effectiveness(primary_action, context),
                "is_primary": True
            }
        ]
        
        # Generate alternative recommendations
        risk_score = context["risk_score"]
        
        # Alternative 1: More restrictive
        if primary_action == "allow":
            alt_action = "challenge" if risk_score > 20 else "delay"
            recommendations.append({
                "action": alt_action,
                "reason": f"More restrictive alternative for risk score {risk_score}",
                "confidence": max(0.1, primary_confidence - 0.3),
                "effectiveness": self._predict_effectiveness(alt_action, context),
                "is_primary": False
            })
        
        # Alternative 2: Less restrictive
        if primary_action in ["block", "challenge"]:
            alt_action = "challenge" if primary_action == "block" else "delay"
            recommendations.append({
                "action": alt_action,
                "reason": f"Less restrictive alternative",
                "confidence": max(0.1, primary_confidence - 0.2),
                "effectiveness": self._predict_effectiveness(alt_action, context),
                "is_primary": False
            })
        
        return recommendations
    
    def retrain_model(self, feedback_data: List[Dict[str, Any]]):
        """Retrain healing model based on feedback"""
        try:
            # Analyze feedback to improve decision making
            successful_actions = []
            failed_actions = []
            
            for feedback in feedback_data:
                if feedback.get("success", False):
                    successful_actions.append(feedback)
                else:
                    failed_actions.append(feedback)
            
            # Update effectiveness scores based on feedback
            for action_type in self.effectiveness_scores:
                successful_count = sum(1 for f in successful_actions if f.get("action") == action_type)
                failed_count = sum(1 for f in failed_actions if f.get("action") == action_type)
                total_count = successful_count + failed_count
                
                if total_count > 0:
                    success_rate = successful_count / total_count
                    # Adjust effectiveness score (learning rate = 0.1)
                    self.effectiveness_scores[action_type] = (
                        0.9 * self.effectiveness_scores[action_type] + 0.1 * success_rate
                    )
            
            logger.info(f"Retrained healing model with {len(feedback_data)} feedback samples")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")