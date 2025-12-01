"""
Database Model Tests
"""
import pytest
from datetime import date, datetime
from models import (
    VendorInvoice,
    PlexInvoice,
    PurchaseOrder,
    SyncOperation,
    User,
    AuditLog
)


def test_create_vendor_invoice(session):
    """Test creating vendor invoice"""
    invoice = VendorInvoice(
        invoice_number="INV-001",
        vendor_name="Test Vendor",
        invoice_date=date(2024, 1, 15),
        total_amount=1000.00,
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=12345,
        po_numbers=["PO-001"],
        status="received"
    )

    session.add(invoice)
    session.commit()
    session.refresh(invoice)

    assert invoice.id is not None
    assert invoice.invoice_number == "INV-001"
    assert invoice.created_at is not None


def test_vendor_invoice_with_line_items(session):
    """Test invoice with JSON line items"""
    line_items = [
        {
            "line_number": 1,
            "description": "Item A",
            "quantity": 10,
            "unit_price": 50.00,
            "line_total": 500.00
        },
        {
            "line_number": 2,
            "description": "Item B",
            "quantity": 5,
            "unit_price": 100.00,
            "line_total": 500.00
        }
    ]

    invoice = VendorInvoice(
        invoice_number="INV-002",
        vendor_name="Test Vendor",
        total_amount=1000.00,
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=12345,
        line_items=line_items
    )

    session.add(invoice)
    session.commit()
    session.refresh(invoice)

    assert len(invoice.line_items) == 2
    assert invoice.line_items[0]["description"] == "Item A"


def test_create_plex_invoice(session):
    """Test creating Plex invoice"""
    plex_invoice = PlexInvoice(
        plex_invoice_id="plex-12345",
        invoice_number="RECEIVED",
        po_number="PO-001",
        vendor_name="Test Vendor",
        total_amount=1000.00,
        status="received"
    )

    session.add(plex_invoice)
    session.commit()
    session.refresh(plex_invoice)

    assert plex_invoice.id is not None
    assert plex_invoice.invoice_number == "RECEIVED"


def test_create_purchase_order(session):
    """Test creating purchase order"""
    po = PurchaseOrder(
        po_number="PO-001",
        vendor_name="Test Vendor",
        po_type="standard",
        total_amount=1000.00,
        status="open",
        line_items=[
            {
                "line_number": 1,
                "part_number": "PART-001",
                "quantity": 10,
                "unit_price": 100.00
            }
        ]
    )

    session.add(po)
    session.commit()
    session.refresh(po)

    assert po.id is not None
    assert len(po.line_items) == 1


def test_sync_operation(session):
    """Test sync operation tracking"""
    # Create vendor invoice
    vendor_invoice = VendorInvoice(
        invoice_number="INV-001",
        vendor_name="Test Vendor",
        total_amount=1000.00,
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=12345
    )
    session.add(vendor_invoice)
    session.commit()

    # Create plex invoice
    plex_invoice = PlexInvoice(
        plex_invoice_id="plex-12345",
        invoice_number="RECEIVED",
        po_number="PO-001",
        total_amount=1000.00
    )
    session.add(plex_invoice)
    session.commit()

    # Create sync operation
    sync_op = SyncOperation(
        vendor_invoice_id=vendor_invoice.id,
        plex_invoice_id=plex_invoice.id,
        operation_type="update_invoice_number",
        confidence_before=85.0,
        confidence_after=95.0,
        success=True,
        processing_time_ms=1234
    )

    session.add(sync_op)
    session.commit()
    session.refresh(sync_op)

    assert sync_op.id is not None
    assert sync_op.success is True
    assert sync_op.confidence_after > sync_op.confidence_before


def test_user_model(session):
    """Test user creation"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password_here",
        role="user",
        can_approve=False
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.is_active is True
    assert user.login_count == 0


def test_audit_log(session):
    """Test audit log creation"""
    audit = AuditLog(
        user_id=1,
        user_email="test@example.com",
        action="upload_invoice",
        entity_type="vendor_invoice",
        entity_id=1,
        before_data={},
        after_data={"invoice_number": "INV-001"},
        success=True
    )

    session.add(audit)
    session.commit()
    session.refresh(audit)

    assert audit.id is not None
    assert audit.action == "upload_invoice"

