"""Authentication and authorization"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .config import settings

# Security settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate user"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    return schemas.User(
        id=user.id,
        username=user.username,
        role=user.role,
        vendor_id=user.vendor_id
    )


def create_demo_users(db: Session):
    """Create demo users for testing with all ABAC roles"""
    demo_users = [
        {
            "username": "admin",
            "password": "admin123",
            "full_name": "System Administrator",
            "email": "admin@qapishield.com",
            "role": "admin",
            "vendor_id": None
        },
        {
            "username": "employee",
            "password": "emp123",
            "full_name": "Bank Employee",
            "email": "employee@qapishield.com",
            "role": "employee",
            "vendor_id": None
        },
        {
            "username": "auditor",
            "password": "audit123",
            "full_name": "Audit Officer",
            "email": "auditor@qapishield.com",
            "role": "auditor",
            "vendor_id": None
        },
        {
            "username": "vendor1",
            "password": "vendor123",
            "full_name": "Vendor User 1",
            "email": "vendor1@example.com",
            "role": "vendor",
            "vendor_id": "vendor_001"
        },
        {
            "username": "customer",
            "password": "cust123",
            "full_name": "Retail Banking Customer",
            "email": "customer@example.com",
            "role": "customer",
            "vendor_id": None
        },
        {
            "username": "guest",
            "password": "guest123",
            "full_name": "Guest User",
            "email": "guest@example.com",
            "role": "guest",
            "vendor_id": None
        },
        {
            "username": "external",
            "password": "ext123",
            "full_name": "External Partner",
            "email": "external@qapishield.com",
            "role": "external",
            "vendor_id": None
        }
    ]

    for user_data in demo_users:
        existing_user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
        if not existing_user:
            user = models.User(
                username=user_data["username"],
                full_name=user_data["full_name"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                vendor_id=user_data["vendor_id"]
            )
            db.add(user)

    db.commit()
