"""
Sync API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from models import VendorInvoice, PlexInvoice, SyncOperation, PurchaseOrder
from db.session import get_session
from api.auth import get_current_user, User
from core.plex_client import plex_client
from core.matcher import po_matcher
from core.learning import learning_system
from datetime import datetime, timezone
from loguru import logger

router = APIRouter()


class SyncRequest(BaseModel):
    vendor_invoice_id: int
    po_number: str


@router.post("")
async def sync_invoice(
    request: SyncRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Sync vendor invoice to Plex"""
    # Get vendor invoice
    vendor_invoice = session.get(VendorInvoice, request.vendor_invoice_id)
    if not vendor_invoice:
        raise HTTPException(status_code=404, detail="Vendor invoice not found")
    
    # Get PO
    po = session.exec(select(PurchaseOrder).where(PurchaseOrder.po_number == request.po_number)).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Find or create Plex invoice
    plex_invoice = session.exec(
        select(PlexInvoice).where(PlexInvoice.po_number == request.po_number)
    ).first()
    
    if not plex_invoice:
        # Create new Plex invoice record
        plex_invoice = PlexInvoice(
            plex_invoice_id="pending",
            invoice_number="RECEIVED",
            po_number=request.po_number,
            vendor_name=vendor_invoice.vendor_name,
            total_amount=vendor_invoice.total_amount,
            status="received"
        )
        session.add(plex_invoice)
        session.commit()
        session.refresh(plex_invoice)
    
    # Create sync operation
    sync_op = SyncOperation(
        vendor_invoice_id=vendor_invoice.id,
        plex_invoice_id=plex_invoice.id,
        operation_type="update_invoice_number",
        confidence_before=vendor_invoice.confidence_score,
        user_id=current_user.id
    )
    
    start_time = datetime.now(timezone.utc)
    
    try:
        # Sync to Plex
        result = await plex_client.sync_invoice(
            vendor_invoice_number=vendor_invoice.invoice_number,
            po_number=request.po_number
        )
        
        if result["success"]:
            # Update Plex invoice
            plex_invoice.invoice_number = vendor_invoice.invoice_number
            plex_invoice.last_synced_at = datetime.now(timezone.utc)
            plex_invoice.sync_status = "synced"
            session.add(plex_invoice)
            
            # Update sync operation
            sync_op.success = True
            sync_op.confidence_after = vendor_invoice.confidence_score
            sync_op.after_data = result.get("updated_invoice", {})
            sync_op.po_type = po.po_type
            sync_op.vendor_pattern = vendor_invoice.vendor_name
            
            # Learn from sync
            learning_system.learn_from_sync_operation(sync_op)
            
            logger.success(f"Successfully synced invoice {vendor_invoice.invoice_number}")
        else:
            sync_op.success = False
            sync_op.error_message = result.get("message", "Unknown error")
            plex_invoice.sync_status = "failed"
            session.add(plex_invoice)
            logger.error(f"Sync failed: {result.get('message')}")
        
    except Exception as e:
        sync_op.success = False
        sync_op.error_message = str(e)
        logger.error(f"Sync exception: {e}")
    
    # Calculate processing time
    end_time = datetime.now(timezone.utc)
    sync_op.processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
    
    session.add(sync_op)
    session.commit()
    session.refresh(sync_op)
    
    return {
        "success": sync_op.success,
        "sync_operation_id": sync_op.id,
        "message": sync_op.error_message or "Sync completed successfully"
    }

