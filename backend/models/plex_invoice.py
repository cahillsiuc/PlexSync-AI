"""
Plex Invoice Model - Represents invoices in Plex ERP
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import date, datetime
from .base import BaseModel

class PlexInvoice(BaseModel, table=True):
    """Invoice from Plex ERP system"""
    __tablename__ = "plex_invoices"

    # Plex IDs
    plex_invoice_id: str = Field(unique=True, index=True)
    invoice_number: str = Field(index=True)  # Could be "RECEIVED" initially

    # PO Reference
    po_number: str = Field(index=True)

    # Vendor
    vendor_code: Optional[str] = None
    vendor_name: Optional[str] = None

    # Amounts
    total_amount: Optional[float] = None

    # Status
    status: str = Field(default="received")  # received, posted, paid

    # Dates
    invoice_date: Optional[date] = None
    received_date: Optional[date] = None
    posted_date: Optional[date] = None

    # Raw Plex data (for reference)
    plex_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Sync tracking
    last_synced_at: Optional[datetime] = None
    sync_status: str = "pending"  # pending, synced, failed

