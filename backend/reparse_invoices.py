"""
Re-parse existing invoices with updated OpenAI model
Updates existing invoices (no duplicates)
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import Session, engine, create_db_and_tables
from models import VendorInvoice
from sqlmodel import select, or_
from core.ai_parser import ai_parser
from loguru import logger
from config import settings
from datetime import date
from dateutil.parser import parse as parse_date

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


async def reparse_invoices():
    """Re-parse invoices that failed or have low confidence"""
    print("\n" + "="*60)
    print("🔄 Re-parsing Invoices with Updated Model")
    print("="*60)
    print(f"\n📋 Using model: {settings.openai_model}")
    
    session = Session(engine)
    
    try:
        # Find invoices that need re-parsing
        # - Status is "parsed" but confidence is 0
        # - Status is "failed"
        # - Status is "received" (never parsed)
        
        invoices_to_reparse = session.exec(
            select(VendorInvoice).where(
                or_(
                    (VendorInvoice.status == "parsed") & (VendorInvoice.confidence_score == 0.0),
                    VendorInvoice.status == "failed",
                    VendorInvoice.status == "received"
                )
            )
        ).all()
        
        if not invoices_to_reparse:
            print("\n✅ No invoices need re-parsing!")
            return
        
        print(f"\n📬 Found {len(invoices_to_reparse)} invoice(s) to re-parse:")
        for inv in invoices_to_reparse:
            print(f"   - Invoice {inv.id}: {inv.invoice_number} ({inv.status}, {inv.confidence_score}% confidence)")
        
        print(f"\n🔄 Starting re-parsing...\n")
        
        success_count = 0
        failed_count = 0
        
        for invoice in invoices_to_reparse:
            try:
                print(f"📄 Processing invoice {invoice.id}: {invoice.invoice_number or 'PENDING'}")
                
                # Check if file exists
                if not Path(invoice.file_path).exists():
                    print(f"   ⚠️  File not found: {invoice.file_path}")
                    failed_count += 1
                    continue
                
                # Re-parse with updated model
                parsed_data = await ai_parser.parse_invoice(invoice.file_path)
                
                # Check if parsing was successful
                if "error" in parsed_data:
                    print(f"   ❌ Parsing failed: {parsed_data.get('error', 'Unknown error')}")
                    invoice.status = "failed"
                    invoice.parsed_data = parsed_data
                    session.add(invoice)
                    session.commit()
                    failed_count += 1
                    continue
                
                # Update invoice with parsed data
                invoice.invoice_number = parsed_data.get("invoice_number", invoice.invoice_number or "PENDING")
                invoice.vendor_name = parsed_data.get("vendor_name", invoice.vendor_name or "PENDING")
                
                # Convert date strings to date objects
                invoice_date_str = parsed_data.get("invoice_date")
                if invoice_date_str:
                    try:
                        if isinstance(invoice_date_str, str):
                            invoice.invoice_date = parse_date(invoice_date_str).date()
                        elif isinstance(invoice_date_str, date):
                            invoice.invoice_date = invoice_date_str
                    except:
                        invoice.invoice_date = None
                
                due_date_str = parsed_data.get("due_date")
                if due_date_str:
                    try:
                        if isinstance(due_date_str, str):
                            invoice.due_date = parse_date(due_date_str).date()
                        elif isinstance(due_date_str, date):
                            invoice.due_date = due_date_str
                    except:
                        invoice.due_date = None
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
                
                print(f"   ✅ Successfully parsed: {invoice.invoice_number} ({invoice.confidence_score}% confidence)")
                print(f"      Vendor: {invoice.vendor_name}")
                if invoice.total_amount:
                    print(f"      Amount: ${invoice.total_amount:,.2f}")
                if invoice.po_numbers:
                    print(f"      PO Numbers: {', '.join(invoice.po_numbers)}")
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error re-parsing invoice {invoice.id}: {e}")
                session.rollback()  # Rollback before updating status
                try:
                    invoice.status = "failed"
                    session.add(invoice)
                    session.commit()
                except:
                    session.rollback()
                failed_count += 1
                continue
        
        print("\n" + "="*60)
        print("✅ Re-parsing Complete")
        print("="*60)
        print(f"\n📊 Results:")
        print(f"   ✅ Successfully parsed: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📦 Total processed: {len(invoices_to_reparse)}")
        
    except Exception as e:
        logger.error(f"Error in re-parsing: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


async def main():
    """Main function"""
    print("\n" + "="*60)
    print("PlexSync AI - Invoice Re-parsing Tool")
    print("="*60)
    
    # Initialize database
    print("\n📦 Initializing database...")
    create_db_and_tables()
    print("✅ Database initialized")
    
    # Re-parse invoices
    await reparse_invoices()
    
    print("\n💡 Next steps:")
    print("   1. Check the dashboard to see updated invoice data")
    print("   2. Review parsed invoices for accuracy")
    print("   3. Proceed with sync to Plex ERP if confidence is high")


if __name__ == "__main__":
    asyncio.run(main())

