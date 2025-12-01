"""
Sync API Endpoint Tests
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys

# Mock config before importing
mock_settings = MagicMock()
mock_settings.plex_api_url = "https://api.plex.test"
mock_settings.plex_api_key = "test-key"
mock_settings.plex_timeout = 30
mock_settings.plex_retry_attempts = 3
mock_settings.plex_invoice_endpoint = "/ap-invoices"
mock_settings.plex_po_endpoint = "/purchase-orders"

sys.modules['config'] = MagicMock(settings=mock_settings)

from models import VendorInvoice, PlexInvoice, PurchaseOrder


def test_sync_invoice_endpoint(
    authenticated_client,
    session,
    sample_invoice_data,
    sample_plex_invoice
):
    """Test POST /api/sync endpoint"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    # Create vendor invoice
    vendor_invoice = VendorInvoice(
        invoice_number=sample_invoice_data["invoice_number"],
        vendor_name=sample_invoice_data["vendor_name"],
        total_amount=sample_invoice_data["total_amount"],
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=1000,
        po_numbers=["PO-2024-100"],
        confidence_score=95.0
    )
    session.add(vendor_invoice)
    session.commit()

    # Create PO
    po = PurchaseOrder(
        po_number="PO-2024-100",
        vendor_name=sample_invoice_data["vendor_name"],
        total_amount=sample_invoice_data["total_amount"],
        status="open"
    )
    session.add(po)
    session.commit()

    # Mock Plex client
    with patch('api.sync.plex_client.sync_invoice', new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = {
            "success": True,
            "updated_invoice": {
                "id": sample_plex_invoice["id"],
                "invoice_number": sample_invoice_data["invoice_number"]
            }
        }

        response = authenticated_client.post(
            "/api/sync",
            json={
                "vendor_invoice_id": vendor_invoice.id,
                "po_number": "PO-2024-100"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sync_operation_id" in data


def test_sync_invoice_not_found(authenticated_client):
    """Test sync with non-existent invoice"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    response = authenticated_client.post(
        "/api/sync",
        json={
            "vendor_invoice_id": 99999,
            "po_number": "PO-FAKE"
        }
    )

    assert response.status_code == 404


def test_sync_invoice_no_po(authenticated_client, session, sample_invoice_data):
    """Test sync with non-existent PO"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    # Create vendor invoice
    vendor_invoice = VendorInvoice(
        invoice_number=sample_invoice_data["invoice_number"],
        vendor_name=sample_invoice_data["vendor_name"],
        total_amount=sample_invoice_data["total_amount"],
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=1000
    )
    session.add(vendor_invoice)
    session.commit()

    response = authenticated_client.post(
        "/api/sync",
        json={
            "vendor_invoice_id": vendor_invoice.id,
            "po_number": "PO-NOT-EXISTS"
        }
    )

    assert response.status_code == 404

