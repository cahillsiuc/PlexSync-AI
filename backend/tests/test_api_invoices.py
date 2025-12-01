"""
Invoice API Endpoint Tests
"""
import pytest
from io import BytesIO
from unittest.mock import AsyncMock, patch, MagicMock
import sys

# Mock config before importing
mock_settings = MagicMock()
mock_settings.storage_path = "./test_storage"
mock_settings.storage_type = "local"
mock_settings.max_file_size_mb = 16
mock_settings.allowed_file_types = ["pdf", "png", "jpg", "jpeg"]
mock_settings.openai_api_key = "test-key"
mock_settings.openai_model = "gpt-4-vision-preview"
mock_settings.openai_max_tokens = 2000
mock_settings.openai_temperature = 0.1

sys.modules['config'] = MagicMock(settings=mock_settings)

from models import VendorInvoice


def test_upload_invoice(authenticated_client, temp_storage):
    """Test invoice upload endpoint"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    # Mock AI parser
    with patch('api.invoices.ai_parser.parse_invoice', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = {
            "invoice_number": "INV-2024-001",
            "vendor_name": "Test Vendor",
            "total_amount": 1000.00,
            "confidence": 95.0
        }
        
        # Create fake PDF
        pdf_content = b"PDF content here"
        files = {
            "file": ("invoice.pdf", BytesIO(pdf_content), "application/pdf")
        }

        response = authenticated_client.post(
            "/api/invoices/upload",
            files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] in ["received", "parsed"]


def test_list_invoices(authenticated_client, session, sample_invoice_data):
    """Test listing invoices"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    # Create test invoice
    invoice = VendorInvoice(
        invoice_number=sample_invoice_data["invoice_number"],
        vendor_name=sample_invoice_data["vendor_name"],
        total_amount=sample_invoice_data["total_amount"],
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=1000
    )
    session.add(invoice)
    session.commit()

    response = authenticated_client.get("/api/invoices")

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["invoice_number"] == sample_invoice_data["invoice_number"]


def test_get_invoice_by_id(authenticated_client, session, sample_invoice_data):
    """Test getting single invoice"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    invoice = VendorInvoice(
        invoice_number=sample_invoice_data["invoice_number"],
        vendor_name=sample_invoice_data["vendor_name"],
        total_amount=sample_invoice_data["total_amount"],
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=1000
    )
    session.add(invoice)
    session.commit()

    response = authenticated_client.get(f"/api/invoices/{invoice.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["invoice_number"] == sample_invoice_data["invoice_number"]


def test_update_invoice(authenticated_client, session, sample_invoice_data):
    """Test updating invoice"""
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    invoice = VendorInvoice(
        invoice_number=sample_invoice_data["invoice_number"],
        vendor_name=sample_invoice_data["vendor_name"],
        total_amount=sample_invoice_data["total_amount"],
        file_path="/storage/test.pdf",
        file_type="pdf",
        file_size=1000
    )
    session.add(invoice)
    session.commit()

    response = authenticated_client.patch(
        f"/api/invoices/{invoice.id}",
        json={"invoice_number": "INV-2024-999", "vendor_name": "Updated Vendor"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["invoice_number"] == "INV-2024-999"
    assert data["vendor_name"] == "Updated Vendor"

