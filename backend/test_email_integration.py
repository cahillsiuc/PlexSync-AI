"""
Test Email Integration
Quick test script to verify email connection and process invoices
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from services.email_service import email_service
from loguru import logger
from db.session import create_db_and_tables

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG"
)


async def test_email_connection():
    """Test IMAP connection"""
    print("\n" + "="*60)
    print("🔍 Testing Email Connection")
    print("="*60)
    
    print(f"\n📧 Email Configuration:")
    print(f"   Provider: {settings.email_provider}")
    print(f"   Server: {settings.email_imap_server}")
    print(f"   Port: {settings.email_imap_port}")
    print(f"   Username: {settings.email_username}")
    print(f"   Enabled: {settings.feature_email_integration}")
    print(f"   Poll Interval: {settings.email_poll_interval}s")
    
    if not settings.email_imap_server:
        print("\n❌ ERROR: EMAIL_IMAP_SERVER not configured in .env")
        return False
    
    if not settings.email_username:
        print("\n❌ ERROR: EMAIL_USERNAME not configured in .env")
        return False
    
    if not settings.email_password and not settings.email_app_password:
        print("\n❌ ERROR: EMAIL_PASSWORD or EMAIL_APP_PASSWORD not configured in .env")
        return False
    
    print("\n🔌 Attempting IMAP connection...")
    
    # Test connection
    if email_service._connect_imap():
        print("✅ IMAP connection successful!")
        email_service._disconnect_imap()
        return True
    else:
        print("❌ IMAP connection failed")
        return False


async def test_email_processing(process_all: bool = False):
    """Test processing emails for invoices"""
    print("\n" + "="*60)
    print("📬 Testing Email Processing")
    print("="*60)
    
    if process_all:
        print("\n⚠️  Processing ALL emails (including already read)")
        print("   This will check all emails in inbox, not just unread")
    else:
        print("\n🔍 Checking inbox for NEW (unread) invoices...")
    
    try:
        # If process_all, temporarily modify the email service to check all emails
        if process_all:
            original_check = email_service.check_emails
            
            async def check_all_emails():
                """Check all emails, not just unread"""
                if not email_service.enabled:
                    return 0
                
                if settings.email_provider != "imap":
                    logger.warning(f"Email provider '{settings.email_provider}' not yet implemented")
                    return 0
                
                if not email_service._connect_imap():
                    return 0
                
                processed_count = 0
                
                try:
                    status, messages = email_service.imap.select(settings.email_inbox_folder)
                    if status != "OK":
                        logger.error(f"Failed to select inbox folder: {settings.email_inbox_folder}")
                        return 0
                    
                    # Search for ALL emails (not just UNSEEN)
                    status, message_ids = email_service.imap.search(None, "ALL")
                    if status != "OK":
                        logger.warning("Failed to search for emails")
                        return 0
                    
                    message_id_list = message_ids[0].split()
                    
                    if not message_id_list:
                        logger.debug("No emails found")
                        return 0
                    
                    print(f"   Found {len(message_id_list)} email(s) in inbox")
                    
                    # Process emails (same logic as check_emails but for all emails)
                    # Import the processing logic
                    from services.email_service import EmailService
                    import email
                    from email.header import decode_header
                    from email.utils import parsedate_to_datetime
                    
                    for msg_id in message_id_list:
                        try:
                            status, msg_data = email_service.imap.fetch(msg_id, "(RFC822)")
                            if status != "OK":
                                continue
                            
                            email_body = msg_data[0][1]
                            msg = email.message_from_bytes(email_body)
                            
                            email_from = email_service._decode_mime_words(msg.get("From", ""))
                            email_subject = email_service._decode_mime_words(msg.get("Subject", ""))
                            email_message_id = msg.get("Message-ID", "")
                            
                            attachments = email_service._extract_attachments(msg)
                            
                            if not attachments:
                                continue
                            
                            print(f"   📎 Found {len(attachments)} attachment(s) in: {email_subject[:50]}")
                            
                            for attachment in attachments:
                                invoice = await email_service._process_invoice_from_email(
                                    email_from=email_from,
                                    email_subject=email_subject,
                                    email_message_id=email_message_id,
                                    attachment_data=attachment
                                )
                                
                                if invoice:
                                    processed_count += 1
                                    
                        except Exception as e:
                            logger.error(f"Error processing email {msg_id}: {e}")
                            continue
                    
                except Exception as e:
                    logger.error(f"Error checking emails: {e}")
                finally:
                    email_service._disconnect_imap()
                
                return processed_count
            
            # Use the modified function
            count = await check_all_emails()
        else:
            count = await email_service.check_emails()
        
        if count > 0:
            print(f"\n✅ Successfully processed {count} invoice(s) from email!")
            print(f"   Check the dashboard to see the new invoices.")
        else:
            print("\n⚠️  No invoices found")
            if not process_all:
                print("   💡 Tip: Emails may already be read. Try with --all flag to process all emails")
        
        return count
        
    except Exception as e:
        print(f"\n❌ Error processing emails: {e}")
        import traceback
        traceback.print_exc()
        return 0


async def main():
    """Main test function"""
    import sys
    
    process_all = "--all" in sys.argv or "-a" in sys.argv
    
    print("\n" + "="*60)
    print("🧪 PlexSync AI - Email Integration Test")
    print("="*60)
    
    # Initialize database
    print("\n📦 Initializing database...")
    create_db_and_tables()
    print("✅ Database initialized")
    
    # Test connection
    connection_ok = await test_email_connection()
    
    if not connection_ok:
        print("\n❌ Email connection test failed. Please check your .env configuration.")
        print("\n💡 Common issues:")
        print("   - Wrong server/port")
        print("   - Incorrect username/password")
        print("   - For Gmail: Need to use App Password, not regular password")
        print("   - Firewall blocking IMAP port 993")
        return
    
    # Test processing
    await test_email_processing(process_all=process_all)
    
    print("\n" + "="*60)
    print("✅ Email Integration Test Complete")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. Check the dashboard for processed invoices")
    print("   2. The email worker will continue polling automatically")
    print("   3. Send a test email with invoice attachment to verify")
    if not process_all:
        print("   4. Run with --all flag to process all emails (including read ones)")


if __name__ == "__main__":
    asyncio.run(main())

