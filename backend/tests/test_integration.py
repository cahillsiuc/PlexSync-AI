"""
End-to-End Integration Tests
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
mock_settings.plex_api_url = "https://api.plex.test"
mock_settings.plex_api_key = "test-key"
mock_settings.plex_timeout = 30
mock_settings.plex_retry_attempts = 3
mock_settings.plex_invoice_endpoint = "/ap-invoices"
mock_settings.plex_po_endpoint = "/purchase-orders"

sys.modules['config'] = MagicMock(settings=mock_settings)


@pytest.mark.integration
def test_full_invoice_workflow(authenticated_client, temp_storage):
    """
    Test complete workflow:
    1. Upload invoice
    2. AI parses it
    3. Match to PO
    4. Sync to Plex
    """
    if authenticated_client is None:
        pytest.skip("main.py not yet created")
    
    from models import VendorInvoice, PurchaseOrder, SyncOperation

    # Step 1: Upload invoice
    pdf_content = b"PDF invoice content"
    files = {
        "file": ("invoice.pdf", BytesIO(pdf_content), "application/pdf")
    }

    with patch('api.invoices.ai_parser.parse_invoice', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = {
            "invoice_number": "INV-2024-001",
            "vendor_name": "Acme Corp",
            "total_amount": 1500.00,
            "po_numbers": ["PO-2024-100"],
            "confidence": 95.0
        }

        upload_response = authenticated_client.post(
            "/api/invoices/upload",
            files=files
        )

        assert upload_response.status_code == 200
        invoice_data = upload_response.json()
        invoice_id = invoice_data["id"]

    # Step 2: Get parsed invoice
    get_response = authenticated_client.get(f"/api/invoices/{invoice_id}")
    assert get_response.status_code == 200
    invoice = get_response.json()
    assert invoice["invoice_number"] == "INV-2024-001"

    # Step 3: Create PO (required for sync)
    from db.session import get_session
    session = next(get_session())
    po = PurchaseOrder(
        po_number="PO-2024-100",
        vendor_name="Acme Corp",
        total_amount=1500.00,
        status="open"
    )
    session.add(po)
    session.commit()

    # Step 4: Sync to Plex
    with patch('api.sync.plex_client.sync_invoice', new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = {
            "success": True,
            "updated_invoice": {
                "id": "plex-001",
                "invoice_number": "INV-2024-001"
            }
        }

        sync_response = authenticated_client.post(
            "/api/sync",
            json={
                "vendor_invoice_id": invoice_id,
                "po_number": "PO-2024-100"
            }
        )

        assert sync_response.status_code == 200
        sync_data = sync_response.json()
        assert sync_data["success"] is True

    # Step 5: Verify sync operation was logged
    sync_ops = session.exec(
        "SELECT * FROM sync_operations WHERE vendor_invoice_id = :invoice_id",
        {"invoice_id": invoice_id}
    ).all()
    assert len(sync_ops) > 0

