"""
Webhooks API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from loguru import logger

router = APIRouter()


@router.post("/plex")
async def plex_webhook(request: Request):
    """Receive webhook from Plex ERP"""
    try:
        data = await request.json()
        logger.info(f"Received Plex webhook: {data}")
        
        # Process webhook data
        # This would handle events from Plex like:
        # - New invoice created
        # - Invoice status changed
        # - PO updated
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

