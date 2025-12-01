"""
Sync Operation Model - Tracks invoice sync operations for learning
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class SyncOperation(BaseModel, table=True):
    """Tracks sync operations between vendor invoice and Plex"""
    __tablename__ = "sync_operations"

    # References
    vendor_invoice_id: int = Field(foreign_key="vendor_invoices.id", index=True)
    plex_invoice_id: int = Field(foreign_key="plex_invoices.id", index=True)

    # Operation Details
    operation_type: str  # update_invoice_number, create_invoice, update_line_items

    # Before/After for learning
    before_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    after_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Confidence & Success
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    success: bool = False

    # User Corrections (for ML learning)
    user_corrections: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    correction_count: int = 0

    # Timing
    processing_time_ms: int = 0

    # Error tracking
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: int = 0

    # Learning data
    po_type: Optional[str] = None  # For scenario-specific learning
    vendor_pattern: Optional[str] = None

    # User who performed sync
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")

