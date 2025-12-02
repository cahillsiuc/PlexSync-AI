"""
Email Worker - Background service that polls for emails
This is the PRIMARY DRIVER of the application
"""
import asyncio
from typing import Optional
from config import settings
from services.email_service import email_service
from loguru import logger


class EmailWorker:
    """
    Background worker that continuously polls email inbox
    for new invoices and automatically processes them
    """
    
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def _poll_emails_loop(self):
        """Main loop that polls emails at configured interval"""
        logger.info("📧 Email worker started - checking for invoices via email")
        logger.info(f"   Poll interval: {settings.email_poll_interval} seconds")
        
        while self.running:
            try:
                if settings.feature_email_integration and email_service.enabled:
                    count = await email_service.check_emails()
                    if count > 0:
                        logger.success(f"📬 Processed {count} new invoice(s) from email")
                else:
                    logger.debug("Email integration is disabled")
                    
            except Exception as e:
                logger.error(f"Error in email polling loop: {e}")
            
            # Wait before next check
            await asyncio.sleep(settings.email_poll_interval)

    def start(self):
        """Start the email worker"""
        if self.running:
            logger.warning("Email worker is already running")
            return
        
        if not settings.feature_email_integration:
            logger.info("Email integration is disabled - worker not started")
            return
        
        if not settings.email_imap_server:
            logger.warning("Email IMAP server not configured - worker not started")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._poll_emails_loop())
        logger.success("✅ Email worker started successfully")

    def stop(self):
        """Stop the email worker"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
        logger.info("Email worker stopped")


# Global email worker instance
email_worker = EmailWorker()

