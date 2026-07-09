from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from core.logger import get_logger
from core.config import WEBHOOK_SECRET
from clients.omnivoice_client import pending_jobs

logger = get_logger("WebhookRoutes")
router = APIRouter(prefix="/api/webhook", tags=["Webhooks"])

@router.post("/omnivoice")
async def omnivoice_webhook(
    request: Request,
    x_webhook_secret: Optional[str] = Header(None)
):
    """
    Điểm đón Webhook từ Celery Worker của OmniVoice.
    """
    if x_webhook_secret != WEBHOOK_SECRET:
        logger.warning("Truy cập Webhook trái phép (Sai Secret)")
        raise HTTPException(status_code=403, detail="Forbidden")
        
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
        
    job_id = data.get("job_id")
    status = data.get("status")
    audio_url = data.get("audio_url")
    error_message = data.get("error_message")
    
    logger.info(f"Đã nhận Webhook cho job {job_id}. Status: {status}")
    
    if not job_id:
        return {"status": "ignored", "message": "No job_id"}
        
    # Tìm xem job này có đang được đợi bởi AVStreamer không
    future = pending_jobs.pop(job_id, None)
    
    if future and not future.done():
        if status == "success" and audio_url:
            # Đánh thức Future và truyền URL vào
            future.set_result(audio_url)
        else:
            logger.error(f"OmniVoice báo lỗi cho job {job_id}: {error_message}")
            # Đánh thức Future nhưng trả về None để báo lỗi
            future.set_result(None)
            
    return {"status": "received"}
