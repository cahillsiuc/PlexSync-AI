"""
User Model - Authentication and authorization
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseModel

class User(BaseModel, table=True):
    """Application user"""
    __tablename__ = "users"

    # Identity
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None

    # Authentication
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

    # Role-based access
    role: str = "user"  # user, manager, admin

    # Permissions
    can_approve: bool = False
    can_reject: bool = False
    can_edit: bool = True
    can_view_analytics: bool = True

    # Activity
    last_login: Optional[datetime] = None
    login_count: int = 0

    # Preferences
    email_notifications: bool = True
    auto_approve_threshold: float = 95.0

