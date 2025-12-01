"""
Purchase Order Model - Stores PO data from Plex
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import date
from .base import BaseModel

class PurchaseOrder(BaseModel, table=True):
    """Purchase Order from Plex ERP"""
    __tablename__ = "purchase_orders"

    # PO Identification
    po_number: str = Field(unique=True, index=True)
    plex_po_id: Optional[str] = None

    # Vendor
    vendor_code: Optional[str] = None
    vendor_name: str = Field(index=True)

    # PO Type (for scenario handling)
    po_type: str = "standard"  # standard, blanket, service, freight

    # Dates
    po_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None

    # Amounts
    total_amount: float
    currency: str = "USD"

    # Status
    status: str = Field(default="open")  # open, partial, closed, cancelled

    # Line Items (JSON array)
    line_items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Received quantities tracking
    received_items: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Raw Plex data
    plex_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Metadata
    department: Optional[str] = None
    project_code: Optional[str] = None
    notes: Optional[str] = None

