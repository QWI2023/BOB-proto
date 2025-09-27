"""ABAC Engine - Attribute Based Access Control for QAPIShield"""

from typing import Dict

class ABACEngine:
    def __init__(self):
        # Example rules — extend as needed
        self.rules = [
            {
                "role": "employee",
                "max_txn_amount": 50000,
                "geo": None,
                "decision": "permit"
            },
            {
                "role": "auditor",
                "allowed_endpoints": ["/logs", "/reports"],
                "geo": "HQ",
                "decision": "permit"
            }
        ]

    def evaluate(self, attributes: Dict) -> Dict:
        """
        Evaluate ABAC policy against provided attributes.
        Returns { "decision": "permit|deny|challenge", "reason": str }
        """
        role = attributes.get("role", "external")
        txn_amount = float(attributes.get("transaction_amount", 0))
        geo = attributes.get("geo_location", "NA")
        endpoint = attributes.get("endpoint", "")

        # Rule: Employee can approve only up to ₹50,000
        if role == "employee" and txn_amount > 50000:
            return {"decision": "deny", "reason": "Employee exceeded ₹50,000 limit"}

        # Rule: Auditor can only read logs/reports from HQ
        if role == "auditor":
            if geo != "HQ":
                return {"decision": "deny", "reason": "Auditor access restricted to HQ"}
            if endpoint not in ["/logs", "/reports"]:
                return {"decision": "deny", "reason": "Auditor can only access logs/reports"}

        # Default allow
        return {"decision": "permit", "reason": "Policy conditions satisfied"}
