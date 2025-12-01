"""
AI Parser Tests
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import sys

# Mock config before importing
mock_settings = MagicMock()
mock_settings.openai_api_key = "test-key"
mock_settings.openai_model = "gpt-4-vision-preview"
mock_settings.openai_max_tokens = 2000
mock_settings.openai_temperature = 0.1

sys.modules['config'] = MagicMock(settings=mock_settings)

from core.ai_parser import AIParser


@pytest.fixture
def sample_pdf_path(temp_storage):
    """Create a sample PDF file for testing"""
    pdf_path = temp_storage / "sample_invoice.pdf"
    pdf_path.write_bytes(b"PDF content here")
    return str(pdf_path)


@pytest.mark.asyncio
async def test_parse_invoice_success(sample_pdf_path):
    """Test successful invoice parsing"""
    parser = AIParser()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='''
        {
            "invoice_number": "INV-2024-001",
            "vendor_name": "Acme Corporation",
            "invoice_date": "2024-01-15",
            "due_date": "2024-02-15",
            "total_amount": 1500.00,
            "po_numbers": ["PO-2024-100"],
            "line_items": [],
            "confidence": 95.0
        }
        '''))
    ]

    with patch.object(parser.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        result = await parser.parse_invoice(sample_pdf_path)

        assert result["invoice_number"] == "INV-2024-001"
        assert result["vendor_name"] == "Acme Corporation"
        assert result["confidence"] == 95.0
        assert len(result["po_numbers"]) == 1


@pytest.mark.asyncio
async def test_parse_invoice_with_line_items(sample_pdf_path):
    """Test parsing invoice with line items"""
    parser = AIParser()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='''
        {
            "invoice_number": "INV-2024-001",
            "vendor_name": "Acme Corporation",
            "invoice_date": "2024-01-15",
            "total_amount": 1000.00,
            "po_numbers": ["PO-2024-100"],
            "line_items": [
                {
                    "line_number": 1,
                    "description": "Widget A",
                    "quantity": 10,
                    "unit_price": 100.00,
                    "line_total": 1000.00
                }
            ],
            "confidence": 92.0
        }
        '''))
    ]

    with patch.object(parser.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        result = await parser.parse_invoice(sample_pdf_path)

        assert len(result["line_items"]) == 1
        assert result["line_items"][0]["description"] == "Widget A"


@pytest.mark.asyncio
async def test_parse_invoice_error_handling(sample_pdf_path):
    """Test error handling in parsing"""
    parser = AIParser()

    with patch.object(parser.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("API Error")

        result = await parser.parse_invoice(sample_pdf_path)

        assert "error" in result
        assert result["confidence"] == 0.0

