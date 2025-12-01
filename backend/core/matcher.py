"""
PO Matcher - Matches vendor invoices to purchase orders
"""
from typing import Dict, Any, List, Optional
from models import VendorInvoice, PurchaseOrder
from loguru import logger


class POMatcher:
    """
    Matches vendor invoices to purchase orders based on:
    - PO numbers extracted from invoice
    - Vendor name matching
    - Amount matching
    - Date matching
    """

    def match_invoice_to_po(
        self,
        invoice: VendorInvoice,
        available_pos: List[PurchaseOrder]
    ) -> Optional[PurchaseOrder]:
        """
        Match invoice to best matching PO

        Args:
            invoice: Vendor invoice to match
            available_pos: List of available purchase orders

        Returns:
            Best matching PO or None
        """
        if not invoice.po_numbers:
            logger.warning(f"Invoice {invoice.invoice_number} has no PO numbers")
            return None

        # Try exact PO number match first
        for po_number in invoice.po_numbers:
            for po in available_pos:
                if po.po_number == po_number:
                    logger.info(f"Exact PO match: {po_number}")
                    return po

        # Try fuzzy matching on PO number
        for po_number in invoice.po_numbers:
            for po in available_pos:
                if self._fuzzy_match_po_number(po_number, po.po_number):
                    logger.info(f"Fuzzy PO match: {po_number} -> {po.po_number}")
                    return po

        # Try vendor name + amount matching
        for po in available_pos:
            if self._match_by_vendor_and_amount(invoice, po):
                logger.info(f"Matched by vendor and amount: {po.po_number}")
                return po

        logger.warning(f"No PO match found for invoice {invoice.invoice_number}")
        return None

    def _fuzzy_match_po_number(self, invoice_po: str, po_number: str) -> bool:
        """Fuzzy match PO numbers (handles variations)"""
        # Normalize: remove spaces, dashes, convert to uppercase
        normalized_invoice = invoice_po.replace(" ", "").replace("-", "").upper()
        normalized_po = po_number.replace(" ", "").replace("-", "").upper()

        # Exact match after normalization
        if normalized_invoice == normalized_po:
            return True

        # Check if one contains the other
        if normalized_invoice in normalized_po or normalized_po in normalized_invoice:
            return True

        return False

    def _match_by_vendor_and_amount(
        self,
        invoice: VendorInvoice,
        po: PurchaseOrder
    ) -> bool:
        """Match by vendor name and amount similarity"""
        # Vendor name match
        vendor_match = (
            invoice.vendor_name.lower() == po.vendor_name.lower() or
            invoice.vendor_name.lower() in po.vendor_name.lower() or
            po.vendor_name.lower() in invoice.vendor_name.lower()
        )

        if not vendor_match:
            return False

        # Amount match (within 5% tolerance)
        if invoice.total_amount and po.total_amount:
            tolerance = po.total_amount * 0.05
            amount_match = abs(invoice.total_amount - po.total_amount) <= tolerance
            return amount_match

        return False

    def calculate_match_confidence(
        self,
        invoice: VendorInvoice,
        po: PurchaseOrder
    ) -> float:
        """
        Calculate confidence score for invoice-PO match

        Returns:
            Confidence score 0-100
        """
        score = 0.0

        # PO number match (50 points)
        if invoice.po_numbers:
            for po_num in invoice.po_numbers:
                if po_num == po.po_number:
                    score += 50.0
                    break
                elif self._fuzzy_match_po_number(po_num, po.po_number):
                    score += 40.0
                    break

        # Vendor name match (30 points)
        if invoice.vendor_name and po.vendor_name:
            if invoice.vendor_name.lower() == po.vendor_name.lower():
                score += 30.0
            elif invoice.vendor_name.lower() in po.vendor_name.lower():
                score += 20.0

        # Amount match (20 points)
        if invoice.total_amount and po.total_amount:
            tolerance = po.total_amount * 0.05
            diff = abs(invoice.total_amount - po.total_amount)
            if diff == 0:
                score += 20.0
            elif diff <= tolerance:
                score += 15.0

        return min(score, 100.0)


# Singleton instance
po_matcher = POMatcher()

