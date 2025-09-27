"""Seed database with demo data for QAPIShield (ABAC aligned)"""
import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models
from backend.auth import create_demo_users


def create_tables():
    """Create database tables"""
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def seed_vendors(db: Session):
    """Seed vendors with ABAC-aligned reputation scores"""
    vendors = [
        {
            "id": "vendor_001",
            "name": "TrustedTech Solutions",
            "reputation_score": 90.0,  # ≥70 → permit
            "is_active": True,
            "public_key": "falcon512_demo_public_key_vendor_001",
        },
        {
            "id": "vendor_002",
            "name": "EuroData Systems",
            "reputation_score": 65.0,  # 50–69 → challenge
            "is_active": True,
            "public_key": "falcon512_demo_public_key_vendor_002",
        },
        {
            "id": "vendor_003",
            "name": "QuickAccess Corp",
            "reputation_score": 40.0,  # <50 → block
            "is_active": True,
            "public_key": "falcon512_demo_public_key_vendor_003",
        },
    ]
    for v in vendors:
        if not db.query(models.Vendor).filter(models.Vendor.id == v["id"]).first():
            db.add(models.Vendor(**v))
    db.commit()
    print(f"✅ Seeded {len(vendors)} vendors")


def seed_sample_requests(db: Session):
    """Seed sample API requests aligned to ABAC rules"""
    endpoints = [
        ("transaction", "POST"),
        ("transaction", "GET"),
        ("customer_kyc", "GET"),
        ("customer_kyc", "UPDATE"),
        ("catalog", "GET"),
        ("payroll", "GET"),
        ("logs", "GET"),
        ("backend_sync", "POST"),
    ]
    roles = ["admin", "employee", "auditor", "vendor", "customer", "guest", "external"]
    vendors = ["vendor_001", "vendor_002", "vendor_003"]

    requests = []
    for _ in range(50):
        role, (resource, method) = random.choice(roles), random.choice(endpoints)
        txn_amount = random.choice([0, 5000, 25000, 75000, 150000])
        request = models.APIRequest(
            endpoint=f"/api/{resource}/{method.lower()}",
            method=method,
            vendor_id=random.choice(vendors) if role == "vendor" else None,
            crypto_valid=random.choice([True, True, False]),
            risk_score=random.uniform(10, 95),
            mitigation_status=random.choice(["permit", "challenge", "block", "delay"]),
            response_time=random.randint(50, 500),
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
            role=role,
            resource_type=resource,
            action=method.lower(),
            transaction_amount=txn_amount,
            sensitivity_level=random.choice(["low", "medium", "high"]),
            device_trust_level=random.choice(["high", "medium", "low"]),
            crypto_mode=random.choice(["classical", "pqc"]),
            geo_location=random.choice(["India", "EU", "USA", "Unknown"]),
        )
        requests.append(request)
    db.add_all(requests)
    db.commit()
    print(f"✅ Seeded {len(requests)} sample API requests")


def seed_anomalies(db: Session):
    """Seed behavioral/statistical anomalies"""
    request_ids = [r.id for r in db.query(models.APIRequest).limit(20).all()]
    anomalies = []
    for _ in range(15):
        anomalies.append(
            models.AnomalyLog(
                request_id=random.choice(request_ids),
                anomaly_type=random.choice(["behavioral", "statistical", "ml_based"]),
                confidence=random.uniform(0.6, 0.95),
                is_anomaly=True,
                details=json.dumps(
                    {
                        "feature_deviation": random.uniform(2.0, 5.0),
                        "threshold": 0.7,
                        "triggered_rules": ["geo_location_change", "failed_login_attempts"],
                    }
                ),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 720)),
            )
        )
    db.add_all(anomalies)
    db.commit()
    print(f"✅ Seeded {len(anomalies)} anomalies")


def seed_shadow_apis(db: Session):
    """Seed undocumented/deprecated endpoints"""
    shadow_apis = [
        {
            "endpoint": "/internal/admin/users",
            "method": "GET",
            "risk_level": "critical",
            "usage_count": 45,
            "discovered_at": datetime.utcnow() - timedelta(hours=2),
            "last_seen": datetime.utcnow() - timedelta(minutes=10),
            "is_documented": False,
        },
        {
            "endpoint": "/legacy/v1/payments",
            "method": "POST",
            "risk_level": "high",
            "usage_count": 23,
            "discovered_at": datetime.utcnow() - timedelta(hours=6),
            "last_seen": datetime.utcnow() - timedelta(minutes=30),
            "is_documented": False,
        },
    ]
    for s in shadow_apis:
        if not db.query(models.ShadowAPI).filter(
            models.ShadowAPI.endpoint == s["endpoint"],
            models.ShadowAPI.method == s["method"],
        ).first():
            db.add(models.ShadowAPI(**s))
    db.commit()
    print(f"✅ Seeded {len(shadow_apis)} shadow APIs")


def seed_healing_logs(db: Session):
    """Seed adaptive self-healing logs"""
    request_ids = [r.id for r in db.query(models.APIRequest).limit(30).all()]
    actions = ["permit", "challenge", "block", "delay", "retrain"]
    logs = []
    for _ in range(40):
        action = random.choice(actions)
        logs.append(
            models.HealingLog(
                request_id=random.choice(request_ids),
                action=action,
                reason=f"Policy-driven {action} due to ABAC/risk engine",
                auto_applied=random.choice([True, True, False]),
                effectiveness=random.uniform(0.6, 0.98),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
            )
        )
    db.add_all(logs)
    db.commit()
    print(f"✅ Seeded {len(logs)} healing logs")


def main():
    print("🛡️ QAPIShield Database Seeding (ABAC Ready)")
    print("=" * 40)
    create_tables()
    db = SessionLocal()
    try:
        # Create all demo users (7 roles from auth.py)
        create_demo_users(db)
        print("✅ Demo users created")

        seed_vendors(db)
        seed_sample_requests(db)
        seed_anomalies(db)
        seed_shadow_apis(db)
        seed_healing_logs(db)

        print("\n🎉 Seeding completed successfully!\n")
        print("Demo Login Credentials:")
        print("- Admin: admin / admin123")
        print("- Employee: employee / emp123")
        print("- Auditor: auditor / audit123")
        print("- Vendor: vendor1 / vendor123")
        print("- Customer: customer / cust123")
        print("- Guest: guest / guest123")
        print("- External: external / ext123")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
