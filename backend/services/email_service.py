"""
Email Service - PRIMARY DRIVER
Handles email integration for automatically receiving and processing invoices
"""
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import base64
from datetime import datetime, timezone
from config import settings
from loguru import logger
from db.session import Session, engine
from models import VendorInvoice
from services.storage_service import storage_service
from core.ai_parser import ai_parser


class EmailService:
    """
    Email service for automatically receiving invoices via email
    Supports IMAP (primary) and Gmail API (future)
    """

    def __init__(self):
        self.enabled = settings.feature_email_integration
        self.imap = None
        self.last_check_time = None

    def _connect_imap(self) -> bool:
        """Connect to IMAP server"""
        if not settings.email_imap_server or not settings.email_username:
            logger.warning("Email IMAP settings not configured")
            return False

        try:
            self.imap = imaplib.IMAP4_SSL(
                settings.email_imap_server,
                settings.email_imap_port
            )
            
            # Use app password if provided, otherwise regular password
            password = settings.email_app_password or settings.email_password
            if not password:
                logger.error("Email password not configured")
                return False
                
            self.imap.login(settings.email_username, password)
            logger.success(f"Connected to IMAP server: {settings.email_imap_server}")
            return True
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return False

    def _disconnect_imap(self):
        """Disconnect from IMAP server"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
            self.imap = None

    def _decode_mime_words(self, s: str) -> str:
        """Decode MIME encoded words in email headers"""
        decoded_parts = decode_header(s)
        decoded_str = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        return decoded_str

    def _extract_attachments(self, msg: email.message.Message) -> List[Dict[str, Any]]:
        """Extract attachments from email message"""
        attachments = []
        
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    filename = self._decode_mime_words(filename)
                    # Check if file extension is allowed
                    ext = Path(filename).suffix[1:].lower() if '.' in filename else ''
                    if ext in settings.email_attachment_extensions:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'payload': part.get_payload(decode=True)
                        })
        
        return attachments

    async def _process_invoice_from_email(
        self,
        email_from: str,
        email_subject: str,
        email_message_id: str,
        attachment_data: Dict[str, Any]
    ) -> Optional[VendorInvoice]:
        """
        Process invoice attachment from email
        This is the core function that drives the entire workflow
        """
        session = Session(engine)
        
        try:
            # Save attachment file
            file_path = storage_service.save_file(
                file_content=attachment_data['payload'],
                file_name=attachment_data['filename']
            )
            
            # Create invoice record
            invoice = VendorInvoice(
                invoice_number="PENDING",
                vendor_name="PENDING",
                file_path=file_path,
                file_type=Path(attachment_data['filename']).suffix[1:].lower(),
                file_size=len(attachment_data['payload']),
                status="received",
                email_from=email_from,
                email_subject=email_subject,
                email_message_id=email_message_id
            )
            
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            
            logger.info(f"Created invoice {invoice.id} from email: {email_subject}")
            
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
                
                logger.success(
                    f"✅ Auto-parsed invoice {invoice.id} from email: "
                    f"{invoice.invoice_number} ({invoice.confidence_score}% confidence)"
                )
                
                return invoice
                
            except Exception as e:
                logger.error(f"AI parsing failed for email invoice {invoice.id}: {e}")
                invoice.status = "failed"
                session.add(invoice)
                session.commit()
                return invoice
                
        except Exception as e:
            logger.error(f"Failed to process invoice from email: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    async def check_emails(self) -> int:
        """
        Check email inbox for new invoices
        Returns number of invoices processed
        """
        if not self.enabled:
            return 0

        if settings.email_provider != "imap":
            logger.warning(f"Email provider '{settings.email_provider}' not yet implemented")
            return 0

        if not self._connect_imap():
            return 0

        processed_count = 0

        try:
            # Select inbox
            status, messages = self.imap.select(settings.email_inbox_folder)
            if status != "OK":
                logger.error(f"Failed to select inbox folder: {settings.email_inbox_folder}")
                return 0

            # Search for unread emails
            # You can customize this search - e.g., search by subject, sender, etc.
            status, message_ids = self.imap.search(None, "UNSEEN")
            if status != "OK":
                logger.warning("Failed to search for emails")
                return 0

            message_id_list = message_ids[0].split()
            
            if not message_id_list:
                logger.debug("No new emails found")
                return 0

            logger.info(f"Found {len(message_id_list)} new email(s)")

            for msg_id in message_id_list:
                try:
                    # Fetch email
                    status, msg_data = self.imap.fetch(msg_id, "(RFC822)")
                    if status != "OK":
                        continue

                    # Parse email
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)

                    # Extract email metadata
                    email_from = self._decode_mime_words(msg.get("From", ""))
                    email_subject = self._decode_mime_words(msg.get("Subject", ""))
                    email_message_id = msg.get("Message-ID", "")
                    email_date = parsedate_to_datetime(msg.get("Date", "")) if msg.get("Date") else None

                    # Check if sender is allowed (if whitelist configured)
                    if settings.email_allowed_senders:
                        allowed_list = [s.strip() for s in settings.email_allowed_senders.split(",") if s.strip()]
                        if allowed_list:
                            sender_email = email_from.split("<")[-1].split(">")[0].strip()
                            if sender_email not in allowed_list:
                                logger.debug(f"Skipping email from unauthorized sender: {email_from}")
                                continue

                    # Extract attachments
                    attachments = self._extract_attachments(msg)

                    if not attachments:
                        logger.debug(f"No invoice attachments found in email: {email_subject}")
                        continue

                    # Process each attachment as a potential invoice
                    for attachment in attachments:
                        logger.info(
                            f"Processing invoice attachment '{attachment['filename']}' "
                            f"from email: {email_subject}"
                        )

                        invoice = await self._process_invoice_from_email(
                            email_from=email_from,
                            email_subject=email_subject,
                            email_message_id=email_message_id,
                            attachment_data=attachment
                        )

                        if invoice:
                            processed_count += 1

                    # Mark email as read (or move to processed folder)
                    try:
                        # Move to processed folder if it exists
                        self.imap.store(msg_id, "+FLAGS", "\\Seen")
                        if settings.email_processed_folder:
                            try:
                                self.imap.copy(msg_id, settings.email_processed_folder)
                                self.imap.store(msg_id, "+FLAGS", "\\Deleted")
                            except:
                                pass  # Folder might not exist
                    except Exception as e:
                        logger.warning(f"Failed to mark email as processed: {e}")

                except Exception as e:
                    logger.error(f"Error processing email {msg_id}: {e}")
                    continue

            # Expunge deleted emails
            try:
                self.imap.expunge()
            except:
                pass

            if processed_count > 0:
                logger.success(f"✅ Processed {processed_count} invoice(s) from email")

        except Exception as e:
            logger.error(f"Error checking emails: {e}")
        finally:
            self._disconnect_imap()

        return processed_count

    async def send_notification(
        self,
        to: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Send notification email
        TODO: Implement SMTP sending
        """
        if not self.enabled:
            return False

        logger.info(f"Sending email to {to}: {subject}")
        # Placeholder for email sending logic (SMTP)
        return True


# Singleton instance
email_service = EmailService()
