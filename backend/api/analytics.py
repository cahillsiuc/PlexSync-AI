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
    ).one() or 0
    
    # Count invoices by status
    pending_sync = session.exec(
        select(func.count(VendorInvoice.id)).where(
            VendorInvoice.status.in_(["received", "parsed", "matched"])
        )
    ).one() or 0
    
    synced = session.exec(
        select(func.count(VendorInvoice.id)).where(VendorInvoice.status == "synced")
    ).one() or 0
    
    failed = session.exec(
        select(func.count(VendorInvoice.id)).where(VendorInvoice.status == "failed")
    ).one() or 0
    
    # Total amount (sum of all invoice amounts)
    total_amount_result = session.exec(
        select(func.sum(VendorInvoice.total_amount))
    ).one()
    total_amount = float(total_amount_result) if total_amount_result else 0.0
    
    # Recent invoices (last 10)
    recent_invoices = session.exec(
        select(VendorInvoice)
        .order_by(VendorInvoice.created_at.desc())
        .limit(10)
    ).all()
    
    return {
        "total_invoices": total_invoices,
        "pending_sync": pending_sync,
        "synced": synced,
        "failed": failed,
        "total_amount": total_amount,
        "recent_invoices": [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "vendor_name": inv.vendor_name,
                "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
                "total_amount": float(inv.total_amount) if inv.total_amount else None,
                "status": inv.status,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
            }
            for inv in recent_invoices
        ]
    }

