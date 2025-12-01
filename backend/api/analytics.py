"""
Analytics API endpoints
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from models import VendorInvoice, SyncOperation
from db.session import get_session
from api.auth import get_current_user, User
from typing import Dict, Any

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    # Total invoices
    total_invoices = session.exec(
        select(func.count(VendorInvoice.id))
    ).one()
    
    # Invoices by status
    status_counts = {}
    for status in ["received", "parsed", "matched", "synced", "failed"]:
        count = session.exec(
            select(func.count(VendorInvoice.id)).where(VendorInvoice.status == status)
        ).one()
        status_counts[status] = count
    
    # Successful syncs
    successful_syncs = session.exec(
        select(func.count(SyncOperation.id)).where(SyncOperation.success == True)
    ).one()
    
    # Total syncs
    total_syncs = session.exec(select(func.count(SyncOperation.id))).one()
    
    # Average confidence
    avg_confidence = session.exec(
        select(func.avg(VendorInvoice.confidence_score))
    ).one() or 0.0
    
    return {
        "total_invoices": total_invoices,
        "status_counts": status_counts,
        "successful_syncs": successful_syncs,
        "total_syncs": total_syncs,
        "sync_success_rate": (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
        "average_confidence": float(avg_confidence)
    }

