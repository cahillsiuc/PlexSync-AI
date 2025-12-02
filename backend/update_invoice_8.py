"""Update invoice 8 with parsed data from Poppler"""
import asyncio
from db.session import Session, engine
from models import VendorInvoice
from sqlmodel import select
from core.ai_parser import ai_parser
from dateutil.parser import parse as parse_date
from datetime import date

session = Session(engine)
inv = session.exec(select(VendorInvoice).where(VendorInvoice.id == 8)).first()

if inv:
    print(f"Updating invoice 8 with Poppler-parsed data...")
    result = asyncio.run(ai_parser.parse_invoice(inv.file_path))
    
    if "error" not in result:
        # Update invoice
        inv.invoice_number = result.get("invoice_number", inv.invoice_number)
        inv.vendor_name = result.get("vendor_name", inv.vendor_name)
        
        # Convert dates
        invoice_date_str = result.get("invoice_date")
        if invoice_date_str:
            try:
                if isinstance(invoice_date_str, str):
                    inv.invoice_date = parse_date(invoice_date_str).date()
                elif isinstance(invoice_date_str, date):
                    inv.invoice_date = invoice_date_str
            except:
                pass
        
        due_date_str = result.get("due_date")
        if due_date_str:
            try:
                if isinstance(due_date_str, str):
                    inv.due_date = parse_date(due_date_str).date()
                elif isinstance(due_date_str, date):
                    inv.due_date = due_date_str
            except:
                pass
        
        inv.total_amount = result.get("total_amount")
        inv.tax_amount = result.get("tax_amount")
        inv.subtotal = result.get("subtotal")
        inv.po_numbers = result.get("po_numbers", [])
        inv.line_items = result.get("line_items", [])
        inv.parsed_data = result
        inv.confidence_score = result.get("confidence", 0.0)
        inv.raw_text = result.get("raw_text", "")
        inv.status = "parsed"
        
        session.add(inv)
        session.commit()
        
        print(f"✅ Updated invoice 8:")
        print(f"   Invoice: {inv.invoice_number}")
        print(f"   Vendor: {inv.vendor_name}")
        print(f"   Amount: ${inv.total_amount:,.2f}")
        print(f"   Confidence: {inv.confidence_score}%")
    else:
        print(f"❌ Error: {result.get('error')}")
else:
    print("Invoice 8 not found")

session.close()

