"""Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str
    role: str
    full_name: str
    permissions: List[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: UserInfo


class User(BaseModel):
    id: int
    username: str
    role: str
    vendor_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class APIRequestSimulation(BaseModel):
    endpoint: str
    method: str = "GET"
    vendor_id: str
    payload: str
    signature: Optional[str] = None
    vendor_reputation: float = 50.0
    endpoint_sensitivity: str = "medium"  # low, medium, high
    request_frequency: int = 1
    geo_location: str = "US"
    response_time: Optional[int] = None


class HealingOverride(BaseModel):
    request_id: int
    action: str  # allow, challenge, block, delay, retrain
    reason: str


class AnomalyResult(BaseModel):
    is_anomaly: bool
    confidence: float
    anomaly_type: str
    details: Dict[str, Any]


class RiskScore(BaseModel):
    score: float
    breakdown: Dict[str, float]
    level: str  # low, medium, high, critical


class HealingAction(BaseModel):
    action: str
    reason: str
    confidence: float
    auto_applied: bool