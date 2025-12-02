"""
Plex ERP API Client
Handles all interactions with Plex REST API
"""
import httpx
from typing import List, Dict, Any, Optional
from config import settings
from loguru import logger
import asyncio

class PlexClient:
    """
    Client for Plex ERP API

    Key Methods:
    - list_invoices_by_po() - Find all Plex invoices for a PO
    - get_received_invoices() - Get invoices with status "RECEIVED"
    - update_invoice_number() - Change invoice number from "RECEIVED" to actual
    - get_purchase_order() - Get PO details
    """

    def __init__(self):
        self.base_url = settings.plex_api_url
        self.api_key = settings.plex_api_key
        self.timeout = settings.plex_timeout
        self.retry_attempts = settings.plex_retry_attempts
        self.api_key_header = getattr(settings, 'plex_api_key_header', 'X-API-Key')

        # Build headers with configurable API key header
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key to appropriate header
        if self.api_key_header.lower() == "authorization":
            # If using Authorization header, might need format like "ApiKey {key}"
            self.headers["Authorization"] = self.api_key
        else:
            # Use custom header name (e.g., X-API-Key, apikey, etc.)
            self.headers[self.api_key_header] = self.api_key

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self.headers,
                        **kwargs
                    )
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPError as e:
                logger.warning(f"Plex API error (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise Exception("Max retry attempts reached")

    async def list_invoices_by_po(
        self,
        po_number: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all AP invoices for a specific PO

        Args:
            po_number: PO number to search
            status: Filter by status (e.g., "new")

        Returns:
            List of invoice records from Plex
        """
        endpoint = settings.plex_invoice_endpoint
        params = {"poNumber": po_number}  # Plex API uses camelCase: poNumber

        if status:
            params["status"] = status

        result = await self._request("GET", endpoint, params=params)
        # Plex API returns array directly, not wrapped in "invoices" key
        if isinstance(result, list):
            return result
        return result.get("invoices", [])

    async def get_received_invoices(
        self,
        po_number: str
    ) -> List[Dict[str, Any]]:
        """
        Get invoices with invoiceNumber = "Received" for a PO
        This is the target invoice we want to update
        
        Based on working API example:
        /accounting/v1/ap-invoices?invoiceNumber=Received&status=new
        """
        endpoint = settings.plex_invoice_endpoint
        params = {
            "poNumber": po_number,  # Filter by PO number
            "invoiceNumber": "Received",  # Find RECEIVED invoices (capital R)
            "status": "new"  # Status filter
        }

        result = await self._request("GET", endpoint, params=params)
        # Plex API returns array directly
        if isinstance(result, list):
            received = result
        else:
            received = result.get("invoices", [])

        logger.info(f"Found {len(received)} RECEIVED invoices for PO {po_number}")
        return received

    async def update_invoice_number(
        self,
        plex_invoice_id: str,
        new_invoice_number: str
    ) -> Dict[str, Any]:
        """
        Update Plex invoice number from "RECEIVED" to vendor invoice number

        Args:
            plex_invoice_id: Internal Plex invoice ID
            new_invoice_number: Vendor's actual invoice number

        Returns:
            Updated invoice data from Plex
        """
        endpoint = f"{settings.plex_invoice_endpoint}/{plex_invoice_id}"

        payload = {
            "invoiceNumber": new_invoice_number  # Plex API uses camelCase
        }

        logger.info(f"Updating Plex invoice {plex_invoice_id} to {new_invoice_number}")

        result = await self._request("PATCH", endpoint, json=payload)

        logger.success(f"Successfully updated invoice number")
        return result

    async def get_purchase_order(
        self,
        po_number: str
    ) -> Dict[str, Any]:
        """Get PO details from Plex"""
        endpoint = settings.plex_po_endpoint
        params = {"pONumber": po_number}  # Plex API uses camelCase: pONumber
        return await self._request("GET", endpoint, params=params)

    async def sync_invoice(
        self,
        vendor_invoice_number: str,
        po_number: str
    ) -> Dict[str, Any]:
        """
        Main sync operation: Find RECEIVED invoice and update its number

        Args:
            vendor_invoice_number: Invoice number from vendor
            po_number: PO number

        Returns:
            {
                "success": bool,
                "updated_invoice": {...},
                "message": str
            }
        """
        try:
            # Step 1: Find RECEIVED invoices for this PO
            received_invoices = await self.get_received_invoices(po_number)

            if not received_invoices:
                return {
                    "success": False,
                    "message": f"No RECEIVED invoices found for PO {po_number}"
                }

            # Step 2: Update the first RECEIVED invoice
            # (In production, you may need more sophisticated matching logic)
            target_invoice = received_invoices[0]
            plex_invoice_id = target_invoice.get("id")  # UUID format from Plex API

            # Step 3: Update invoice number in Plex
            updated_invoice = await self.update_invoice_number(
                plex_invoice_id,
                vendor_invoice_number
            )

            return {
                "success": True,
                "updated_invoice": updated_invoice,
                "message": f"Successfully updated invoice {plex_invoice_id}"
            }

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "error": str(e)
            }


# Singleton instance
plex_client = PlexClient()

