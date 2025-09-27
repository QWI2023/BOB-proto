"""SQLAlchemy models (ABAC-ready)"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, index=True)  # admin, vendor, employee, external, etc.
    vendor_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Vendor(Base):
    """Vendor model"""
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    name = Column(String)
    reputation_score = Column(Float, default=50.0)
    is_active = Column(Boolean, default=True)
    public_key = Column(Text)
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    requests = relationship("APIRequest", back_populates="vendor")


class APIRequest(Base):
    """API Request log (ABAC enriched)"""
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    method = Column(String)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=True)
    crypto_valid = Column(Boolean, default=False)
    risk_score = Column(Float, index=True)
    mitigation_status = Column(String)  # permit, challenge, block, delay
    response_time = Column(Integer)  # milliseconds
    timestamp = Column(DateTime, default=func.now(), index=True)

    # 🔹 ABAC-aligned contextual fields
    role = Column(String, nullable=True)                  # e.g. admin, employee, customer
    resource_type = Column(String, nullable=True)         # e.g. transaction, kyc, logs
    action = Column(String, nullable=True)                # e.g. get, post, update
    transaction_amount = Column(Float, nullable=True)       # for financial APIs
    sensitivity_level = Column(String, nullable=True)     # low, medium, high
    device_trust_level = Column(String, nullable=True) # high, medium, low
    crypto_mode = Column(String, nullable=True)     # classical / pqc
    geo_location = Column(String, nullable=True)      # India, EU, etc.

    # Relationships
    anomaly_logs = relationship("AnomalyLog", back_populates="request")
    healing_logs = relationship("HealingLog", back_populates="request")
    vendor = relationship("Vendor", back_populates="requests")


class AnomalyLog(Base):
    """Anomaly detection log"""
    __tablename__ = "anomaly_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("api_requests.id"))
    anomaly_type = Column(String)  # behavioral, statistical, ml_based
    confidence = Column(Float)
    is_anomaly = Column(Boolean, default=False, index=True)
    details = Column(Text)  # JSON details
    timestamp = Column(DateTime, default=func.now(), index=True)

    # Relationships
    request = relationship("APIRequest", back_populates="anomaly_logs")


class ShadowAPI(Base):
    """Shadow API detection"""
    __tablename__ = "shadow_apis"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    method = Column(String)
    discovered_at = Column(DateTime, default=func.now())
    risk_level = Column(String)  # low, medium, high, critical
    usage_count = Column(Integer, default=1)
    last_seen = Column(DateTime, default=func.now())
    is_documented = Column(Boolean, default=False)


class HealingLog(Base):
    """Self-healing action log"""
    __tablename__ = "healing_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("api_requests.id"))
    action = Column(String)  # permit, challenge, block, delay, retrain
    reason = Column(Text)
    auto_applied = Column(Boolean, default=True)
    effectiveness = Column(Float)  # 0.0 to 1.0
    timestamp = Column(DateTime, default=func.now(), index=True)

    # Relationships
    request = relationship("APIRequest", back_populates="healing_logs")
