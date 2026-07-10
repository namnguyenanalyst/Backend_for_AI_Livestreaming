import asyncio
import re
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from clients.llm_client import llm_client

from core.logger import get_logger

logger = get_logger("LLM_Route")
router = APIRouter(prefix="/api/llm", tags=["LLM"])

class GenerateRequest(BaseModel):
    prompt: str
    instruction_key: Optional[str] = "default"

@router.post("/stream", summary="Test sinh văn bản dạng Streaming")
async def stream_text(req: GenerateRequest, request: Request):
    """
    Endpoint này chỉ gọi Deepseek và trả về luồng văn bản (SSE) để test trên Postman.
    Không gọi qua OmniVoice.
    """
    async def event_generator():
        try:
            async for chunk in llm_client.generate_stream(req.prompt, req.instruction_key):
                if await request.is_disconnected():
                    logger.info("Client đã ngắt kết nối.")
                    break
                yield chunk
        except Exception as e:
            logger.error(f"Lỗi stream: {e}")
            yield f"[Lỗi: {e}]"

    return StreamingResponse(event_generator(), media_type="text/plain")

@router.post("/generate", summary="Sinh văn bản (Trả về 1 lần dạng JSON)")
async def generate_text(req: GenerateRequest):
    """
    Gọi LLM sinh toàn bộ văn bản và trả về ngay trong 1 block JSON.
    Phù hợp để test sinh text mà không cần streaming.
    """
    full_text = await llm_client.generate_text(req.prompt, req.instruction_key)
    return {"status": "success", "text": full_text}

@router.post("/generate-non-stream", summary="Sinh văn bản (Non-streaming)")
async def generate_non_stream(req: GenerateRequest, request: Request):
    """
    Do API SaveGate lỗi streaming với prompt dài, ta dùng Non-streaming.
    Đợi sinh xong toàn bộ văn bản -> Cắt câu -> Stream giả lập về Postman.
    """
    async def event_generator():
        # Gọi non-stream (block cho đến khi sinh xong toàn bộ 5000 từ)
        # Sẽ mất khoảng vài chục giây đến vài phút tùy độ dài
        full_text = await llm_client.generate_text(req.prompt, req.instruction_key)
        
        if await request.is_disconnected():
            logger.info("Client đã ngắt kết nối trong lúc đợi non-stream.")
            return

        # Biểu thức chính quy để tách câu (dấu chấm, chấm hỏi, chấm than)
        # Giữ lại cả dấu câu
        sentences = re.split(r'(?<=[.?!])\s+', full_text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                

            # Giả lập stream trả về Postman (mỗi lần trả về 1 câu)
            yield f"{sentence} "
            
            # Cố ý delay 1 chút để Postman hiển thị lần lượt cho giống streaming
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/plain")
