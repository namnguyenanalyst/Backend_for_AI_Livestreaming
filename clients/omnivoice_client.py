import os
import asyncio
import httpx
from core.logger import get_logger
from core.config import OMNIVOICE_API_URL, WEBHOOK_URL, WEBHOOK_SECRET, DEFAULT_REF_AUDIO

logger = get_logger("OmniVoiceClient")

# Bộ nhớ tạm lưu trữ các Future đang chờ webhook
# Key: job_id (str), Value: asyncio.Future
pending_jobs = {}

class OmniVoiceClient:
    
    @staticmethod
    async def generate_speech(text: str, ref_audio_path: str = None) -> str:
        """
        Gọi API sang OmniVoice và dừng lại chờ đến khi Webhook trả kết quả về.
        Trả về đường dẫn file local chứa audio.
        """
        if ref_audio_path is None:
            from core.config import DEFAULT_REF_AUDIO
            ref_audio_path = DEFAULT_REF_AUDIO
            
        if not os.path.exists(ref_audio_path):
            logger.error(f"Không tìm thấy file mẫu: {ref_audio_path}")
            return None
            
        logger.info(f"Đang gọi OmniVoice tạo Audio cho text: '{text[:30]}...'")
        
        try:
            async with httpx.AsyncClient() as client:
                with open(ref_audio_path, "rb") as f:
                    files = {'ref_audio': (os.path.basename(ref_audio_path), f, 'audio/wav')}
                    data = {
                        'text': text,
                        'webhook_url': WEBHOOK_URL,
                        'webhook_secret': WEBHOOK_SECRET,
                        'language': 'Vietnamese'
                    }
                    
                    response = await client.post(OMNIVOICE_API_URL, data=data, files=files, timeout=10.0)
                    response.raise_for_status()
                    
                    resp_json = response.json()
                    job_id = resp_json.get("job_id")
                    
                    if not job_id:
                        logger.error("API OmniVoice không trả về job_id")
                        return None
                        
                    logger.debug(f"Đã nhận job_id {job_id}. Đang chờ Webhook...")
                    
                    # Tạo một Future và lưu vào bộ nhớ tạm
                    future = asyncio.Future()
                    pending_jobs[job_id] = future
                    
                    # Ngủ đông vòng lặp, chờ webhook gọi future.set_result()
                    # Cài đặt timeout tối đa (VD: 60s) để tránh treo vĩnh viễn nếu Celery lỗi
                    try:
                        audio_url = await asyncio.wait_for(future, timeout=60.0)
                    except asyncio.TimeoutError:
                        logger.error(f"Timeout khi chờ webhook cho job {job_id}")
                        pending_jobs.pop(job_id, None)
                        return None
                        
                    if not audio_url:
                        logger.error(f"Webhook báo lỗi cho job {job_id}")
                        return None
                        
                    # Tải file audio từ URL về thư mục cục bộ
                    return await OmniVoiceClient._download_audio(job_id, audio_url, client)
                    
        except Exception as e:
            logger.error(f"Lỗi khi gọi OmniVoice: {str(e)}")
            return None
            
    @staticmethod
    async def _download_audio(job_id: str, audio_url: str, client: httpx.AsyncClient) -> str:
        """Tải file từ URL về máy"""
        os.makedirs("uploads/temp_audio", exist_ok=True)
        local_path = os.path.abspath(f"uploads/temp_audio/{job_id}.wav")
        
        logger.info(f"Đang tải audio từ {audio_url} về {local_path}")
        response = await client.get(audio_url)
        response.raise_for_status()
        
        with open(local_path, "wb") as f:
            f.write(response.content)
            
        return local_path
