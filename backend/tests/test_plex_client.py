"""
Tests for Plex API Client
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

from core.plex_client import PlexClient


@pytest.mark.asyncio
async def test_get_received_invoices():
    """Test finding RECEIVED invoices"""
    client = PlexClient()

    # Mock the _request method
    with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "invoices": [
                {
                    "id": "plex-001",
                    "invoice_number": "RECEIVED",
                    "po_number": "PO-2024-100",
                    "total_amount": 1500.00
                },
                {
                    "id": "plex-002",
                    "invoice_number": "INV-999",
                    "po_number": "PO-2024-100",
                    "total_amount": 1500.00
                }
            ]
        }

        result = await client.get_received_invoices("PO-2024-100")

        assert len(result) == 1
        assert result[0]["invoice_number"] == "RECEIVED"
        assert result[0]["id"] == "plex-001"


@pytest.mark.asyncio
async def test_update_invoice_number():
    """Test updating invoice number in Plex"""
    client = PlexClient()

    with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "id": "plex-001",
            "invoice_number": "INV-2024-001",
            "po_number": "PO-2024-100",
            "status": "updated"
        }

        result = await client.update_invoice_number(
            plex_invoice_id="plex-001",
            new_invoice_number="INV-2024-001"
        )

        assert result["invoice_number"] == "INV-2024-001"
        assert result["id"] == "plex-001"


@pytest.mark.asyncio
async def test_sync_invoice_success():
    """Test successful invoice sync"""
    client = PlexClient()

    with patch.object(client, 'get_received_invoices', new_callable=AsyncMock) as mock_get:
        with patch.object(client, 'update_invoice_number', new_callable=AsyncMock) as mock_update:
            mock_get.return_value = [
                {
                    "id": "plex-001",
                    "invoice_number": "RECEIVED",
                    "po_number": "PO-2024-100"
                }
            ]

            mock_update.return_value = {
                "id": "plex-001",
                "invoice_number": "INV-2024-001"
            }

            result = await client.sync_invoice(
                vendor_invoice_number="INV-2024-001",
                po_number="PO-2024-100"
            )

            assert result["success"] is True
            assert "updated_invoice" in result
            mock_get.assert_called_once_with("PO-2024-100")
            mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_sync_invoice_no_received():
    """Test sync when no RECEIVED invoices found"""
    client = PlexClient()

    with patch.object(client, 'get_received_invoices', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []

        result = await client.sync_invoice(
            vendor_invoice_number="INV-2024-001",
            po_number="PO-2024-100"
        )

        assert result["success"] is False
        assert "No RECEIVED invoices" in result["message"]

