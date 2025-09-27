"""Configuration settings for QAPIShield"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./qapishield.db"
    
    # Security
    secret_key: str = "qapishield-zero-trust-secret-key-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Risk scoring weights
    crypto_weight: float = 0.4
    vendor_weight: float = 0.25
    anomaly_weight: float = 0.2
    frequency_weight: float = 0.1
    geo_weight: float = 0.05
    
    # Healing thresholds
    high_risk_threshold: int = 80
    medium_risk_threshold: int = 50
    
    # Anomaly detection
    anomaly_threshold: float = 0.7
    
    # Timezone
    timezone: str = "UTC"
    
    class Config:
        env_file = ".env"


settings = Settings()