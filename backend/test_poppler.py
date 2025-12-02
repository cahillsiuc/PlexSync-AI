"""Test Poppler installation with invoice 8"""
import asyncio
from db.session import Session, engine
from models import VendorInvoice
from sqlmodel import select
from core.ai_parser import ai_parser

session = Session(engine)
inv = session.exec(select(VendorInvoice).where(VendorInvoice.id == 8)).first()

if inv:
    print(f"Testing Poppler with invoice 8: {inv.file_path}")
    result = asyncio.run(ai_parser.parse_invoice(inv.file_path))
    
    if "error" not in result:
        print(f"✅ Success! Invoice: {result.get('invoice_number')}")
        print(f"   Confidence: {result.get('confidence', 0)}%")
        print(f"   Vendor: {result.get('vendor_name')}")
        print(f"   Amount: ${result.get('total_amount', 0)}")
    else:
        print(f"❌ Error: {result.get('error')}")
else:
    print("Invoice 8 not found")

