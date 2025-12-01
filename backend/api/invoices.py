"""
Invoice API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional
from models import VendorInvoice
from db.session import get_session
from api.auth import get_current_user, User
from services.storage_service import storage_service
from core.ai_parser import ai_parser
from loguru import logger

router = APIRouter()


@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Upload and parse invoice"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Save file
        file_path = storage_service.save_file(
            file_content=file_content,
            file_name=file.filename
        )
        
        # Create invoice record
        invoice = VendorInvoice(
            invoice_number="PENDING",
            vendor_name="PENDING",
            file_path=file_path,
            file_type=file.filename.split(".")[-1].lower(),
            file_size=len(file_content),
            status="received"
        )
        
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        
        # Parse invoice with AI (async)
        try:
            parsed_data = await ai_parser.parse_invoice(file_path)
            
            # Update invoice with parsed data
            invoice.invoice_number = parsed_data.get("invoice_number", "PENDING")
            invoice.vendor_name = parsed_data.get("vendor_name", "PENDING")
            invoice.invoice_date = parsed_data.get("invoice_date")
            invoice.due_date = parsed_data.get("due_date")
            invoice.total_amount = parsed_data.get("total_amount")
            invoice.tax_amount = parsed_data.get("tax_amount")
            invoice.subtotal = parsed_data.get("subtotal")
            invoice.po_numbers = parsed_data.get("po_numbers", [])
            invoice.line_items = parsed_data.get("line_items", [])
            invoice.parsed_data = parsed_data
            invoice.confidence_score = parsed_data.get("confidence", 0.0)
            invoice.raw_text = parsed_data.get("raw_text", "")
            invoice.status = "parsed"
            
            session.add(invoice)
            session.commit()
            
            logger.success(f"Parsed invoice {invoice.id}: {invoice.invoice_number}")
        except Exception as e:
            logger.error(f"AI parsing failed for invoice {invoice.id}: {e}")
            invoice.status = "failed"
            session.add(invoice)
            session.commit()
        
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "confidence": invoice.confidence_score
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List invoices"""
    query = select(VendorInvoice)
    
    if status:
        query = query.where(VendorInvoice.status == status)
    
    query = query.offset(skip).limit(limit)
    
    invoices = session.exec(query).all()
    return invoices


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get invoice by ID"""
    invoice = session.get(VendorInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/{invoice_id}")
async def update_invoice(
    invoice_id: int,
    invoice_number: Optional[str] = None,
    vendor_name: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update invoice"""
    invoice = session.get(VendorInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice_number:
        invoice.invoice_number = invoice_number
    if vendor_name:
        invoice.vendor_name = vendor_name
    
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    
    return invoice

