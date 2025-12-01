"""
Audit Log Model - Complete audit trail for compliance
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from .base import BaseModel

class AuditLog(BaseModel, table=True):
    """Audit trail for all actions"""
    __tablename__ = "audit_logs"

    # Who
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    user_email: Optional[str] = None

    # What
    action: str = Field(index=True)  # upload, parse, match, sync, approve, reject, edit
    entity_type: str  # vendor_invoice, plex_invoice, sync_operation
    entity_id: int

    # When
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    # Details
    before_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    after_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    changes: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Metadata (renamed to avoid SQLAlchemy conflict)
    extra_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

