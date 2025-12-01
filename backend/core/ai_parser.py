"""
AI Invoice Parser using GPT-4 Vision
Extracts structured data from PDF/image invoices
"""
from openai import AsyncOpenAI
from typing import Dict, Any, List
from pathlib import Path
import base64
from config import settings
from loguru import logger

class AIParser:
    """
    GPT-4 Vision invoice parser

    Extracts:
    - Invoice number
    - Vendor name
    - Invoice date
    - Due date
    - Total amount
    - PO number(s)
    - Line items
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def parse_invoice(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Parse invoice from file

        Returns:
            {
                "invoice_number": str,
                "vendor_name": str,
                "invoice_date": str (YYYY-MM-DD),
                "due_date": str (YYYY-MM-DD),
                "total_amount": float,
                "po_numbers": [str],
                "line_items": [{...}],
                "confidence": float (0-100),
                "raw_text": str
            }
        """
        try:
            # Read file as base64
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode()

            # Determine file type
            file_type = Path(file_path).suffix.lower().replace(".", "")

            # Create prompt
            prompt = self._create_extraction_prompt()

            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured data from invoices."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{file_type};base64,{file_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Parse response
            result = self._parse_response(response)

            logger.success(f"Parsed invoice: {result.get('invoice_number')}")
            return result

        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            return {
                "error": str(e),
                "confidence": 0.0
            }

    def _create_extraction_prompt(self) -> str:
        """Create extraction prompt for GPT-4"""
        return """
Extract the following information from this invoice image:

1. Invoice Number
2. Vendor/Supplier Name
3. Invoice Date (format: YYYY-MM-DD)
4. Due Date (format: YYYY-MM-DD)
5. Total Amount (numeric value only)
6. Tax Amount (if shown)
7. Purchase Order Number(s) - look for "PO", "P.O.", "Order #", etc.
8. Line Items with: description, quantity, unit price, line total

Return the data as a JSON object with this exact structure:
{
    "invoice_number": "...",
    "vendor_name": "...",
    "invoice_date": "YYYY-MM-DD",
    "due_date": "YYYY-MM-DD",
    "total_amount": 0.00,
    "tax_amount": 0.00,
    "subtotal": 0.00,
    "po_numbers": ["PO-123", "PO-456"],
    "line_items": [
        {
            "line_number": 1,
            "description": "...",
            "quantity": 0.00,
            "unit_price": 0.00,
            "line_total": 0.00
        }
    ],
    "raw_text": "all visible text on invoice",
    "confidence": 0-100 (your confidence in the extraction)
}

Important:
- If a field is not found, use null
- For po_numbers, search entire invoice including footer notes
- For line_items, extract ALL items shown
- Confidence should reflect clarity of the image and data
"""

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse GPT-4 response into structured data"""
        content = response.choices[0].message.content

        # Try to extract JSON from response
        import json
        import re

        # Find JSON in response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data

        # Fallback: return raw content
        return {
            "raw_text": content,
            "confidence": 50.0,
            "error": "Could not parse structured data"
        }


# Singleton instance
ai_parser = AIParser()

