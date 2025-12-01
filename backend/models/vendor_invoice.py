"""
Vendor Invoice Model - Stores invoices received from vendors
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import date
from .base import BaseModel

class VendorInvoice(BaseModel, table=True):
    """Invoice received from vendor (email or upload)"""
    __tablename__ = "vendor_invoices"

    # Basic Info
    invoice_number: str = Field(index=True)
    vendor_name: str = Field(index=True)

    # Dates
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None

    # Amounts
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    subtotal: Optional[float] = None

    # PO References
    po_numbers: List[str] = Field(default=[], sa_column=Column(JSON))

    # File Storage
    file_path: str  # Path to original PDF/image
    file_type: str  # pdf, png, jpg, etc.
    file_size: int  # bytes

    # AI Parsing Results
    raw_text: Optional[str] = None
    parsed_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    confidence_score: float = 0.0

    # Line Items (JSON array)
    line_items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Status
    status: str = Field(default="received")  # received, parsed, matched, synced, failed

    # Email Source (if from email)
    email_message_id: Optional[str] = Field(default=None, index=True)
    email_from: Optional[str] = None
    email_subject: Optional[str] = None

    # Metadata (renamed to avoid SQLAlchemy conflict)
    extra_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

