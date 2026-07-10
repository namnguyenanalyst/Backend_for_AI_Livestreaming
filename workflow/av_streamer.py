import asyncio
import re
import os
import json
from mutagen.wave import WAVE
from core.logger import get_logger
from core.redis_client import get_redis
from obs.source import set_text, create_input, play_media, set_media_file, _trigger_media_action
from clients.omnivoice_client import OmniVoiceClient
from clients.llm_client import llm_client
from workflow.subtitle_streamer import SubtitleStreamer

logger = get_logger("AVStreamer")

class AVStreamer:
    """
    Trình quản lý tiến trình Đồng bộ Phụ đề và Giọng nói liên tục (Continuous AV Streaming).
    Sử dụng Redis làm Queue và Prefetching audio.
    """
    # Key templates for Redis
    REDIS_TEXT_QUEUE = "av_stream:text_queue:{scene}"
    REDIS_READY_QUEUE = "av_stream:ready_queue:{scene}"
    REDIS_STATUS = "av_stream:status:{scene}" # 'running' or 'stopped'
    REDIS_LATEST_TEXT = "av_stream:latest_text:{scene}"
    
    @staticmethod
    def _get_audio_duration(file_path: str) -> float:
        try:
            audio = WAVE(file_path)
            return audio.info.length
        except Exception as e:
            logger.error(f"Không thể đọc độ dài audio {file_path}: {e}")
            return 3.0 # Mặc định 3 giây nếu lỗi

    @staticmethod
    async def _auto_generator_task(scene_name: str):
        """
        Luồng 1: Liên tục kiểm tra lượng câu chưa xử lý (trong text_queue và ready_queue).
        Nếu sắp hết (< 5 câu tổng), tự động gọi LLM sinh thêm, cắt thành câu và đẩy vào text_queue.
        """
        redis = await get_redis()
        text_queue_key = AVStreamer.REDIS_TEXT_QUEUE.format(scene=scene_name)
        ready_queue_key = AVStreamer.REDIS_READY_QUEUE.format(scene=scene_name)
        status_key = AVStreamer.REDIS_STATUS.format(scene=scene_name)
        
        logger.info(f"[AutoGenerator] Đã khởi động cho cảnh {scene_name}")
        
        while True:
            status = await redis.get(status_key)
            if status != "running":
                logger.info(f"[AutoGenerator] Trạng thái '{status}', luồng sẽ dừng lại.")
                break
                
            text_len = await redis.llen(text_queue_key)
            ready_len = await redis.llen(ready_queue_key)
            total_len = text_len + ready_len
            
            if total_len < 5:
                logger.info(f"[AutoGenerator] Queue sắp hết (tổng: {total_len}). Đang gọi LLM tạo văn bản mới...")
                # Fetch market context pre-fetch
                from clients.search_client import get_market_context
                context = await get_market_context()
                
                base_prompt = "Act as a Crypto market analyst. Provide an update on today's Bitcoin price and highlight the most significant cryptocurrency news of the week. Compile this into a detailed, highly accurate news report in English. Please write strictly in continuous paragraphs without any markdown, bullet points, or special characters. IMPORTANT: You MUST spell out all numbers, currencies, decimals, and percentages entirely in words instead of using digits (e.g., write 'sixty-five thousand dollars' instead of '$65,000')."
                prompt = f"{context}\n\n{base_prompt}"
                try:
                    full_text = await llm_client.generate_text(prompt, "web3_researcher")
                    if full_text:
                        # Lưu đoạn văn bản vừa sinh ra vào Redis để có thể GET qua API
                        latest_text_key = AVStreamer.REDIS_LATEST_TEXT.format(scene=scene_name)
                        await redis.set(latest_text_key, full_text)
                        
                        clean_text = re.sub(r'\n+', ' ', full_text).strip()
                        raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
                        sentences = [s.strip() for s in raw_sentences if s.strip()]
                        
                        if sentences:
                            await redis.rpush(text_queue_key, *sentences)
                            logger.info(f"[AutoGenerator] Đã tạo và đẩy thêm {len(sentences)} câu vào hàng đợi.")
                except Exception as e:
                    logger.error(f"[AutoGenerator] Lỗi khi gọi LLM: {e}")
                    
            await asyncio.sleep(5) # Kiểm tra mỗi 5 giây

    @staticmethod
    async def _prefetcher_task(scene_name: str, ref_audio_path: str = None):
        """
        Luồng 2: Kéo câu từ text_queue, gọi tạo Audio qua OmniVoice, 
        lưu file lại và đẩy vào ready_queue dưới dạng JSON {text, audio_path}.
        """
        redis = await get_redis()
        text_queue_key = AVStreamer.REDIS_TEXT_QUEUE.format(scene=scene_name)
        ready_queue_key = AVStreamer.REDIS_READY_QUEUE.format(scene=scene_name)
        status_key = AVStreamer.REDIS_STATUS.format(scene=scene_name)
        
        logger.info(f"[Prefetcher] Đã khởi động cho cảnh {scene_name}")
        
        while True:
            status = await redis.get(status_key)
            if status != "running":
                logger.info(f"[Prefetcher] Trạng thái '{status}', luồng sẽ dừng lại.")
                break
                
            sentence = await redis.lpop(text_queue_key)
            if not sentence:
                await asyncio.sleep(1) # Chờ nếu text_queue đang rỗng
                continue
                
            logger.info(f"[Prefetcher] Bắt đầu tạo audio cho câu: {sentence[:30]}...")
            try:
                if ref_audio_path:
                    audio_path = await OmniVoiceClient.generate_speech(sentence, ref_audio_path=ref_audio_path)
                else:
                    audio_path = await OmniVoiceClient.generate_speech(sentence)
                    
                if audio_path and os.path.exists(audio_path):
                    ready_item = json.dumps({
                        "text": sentence,
                        "audio_path": audio_path
                    })
                    await redis.rpush(ready_queue_key, ready_item)
                    logger.info(f"[Prefetcher] Đã tạo xong audio và đẩy vào ready_queue.")
                else:
                    logger.error(f"[Prefetcher] Lỗi: Không nhận được file audio hợp lệ.")
            except Exception as e:
                logger.error(f"[Prefetcher] Lỗi quá trình tạo Audio: {e}")
                await asyncio.sleep(1)

    @staticmethod
    async def _streamer_task(scene_name: str, text_source_name: str, media_source_name: str):
        """
        Luồng 3: Kéo từ ready_queue, đẩy text và audio lên OBS, 
        ngủ theo thời lượng audio, sau đó xóa file rác.
        """
        redis = await get_redis()
        ready_queue_key = AVStreamer.REDIS_READY_QUEUE.format(scene=scene_name)
        status_key = AVStreamer.REDIS_STATUS.format(scene=scene_name)
        
        logger.info(f"[Streamer] Đã khởi động cho cảnh {scene_name}")
        
        while True:
            status = await redis.get(status_key)
            if status != "running":
                logger.info(f"[Streamer] Trạng thái '{status}', luồng sẽ dừng lại.")
                set_text(text_source_name, "") # Xóa chữ trên màn hình khi kết thúc
                break
                
            ready_item_str = await redis.lpop(ready_queue_key)
            if not ready_item_str:
                await asyncio.sleep(1) # Chờ có audio sẵn sàng
                continue
                
            try:
                ready_item = json.loads(ready_item_str)
                sentence = ready_item.get("text", "")
                audio_path = ready_item.get("audio_path", "")
                
                if not os.path.exists(audio_path):
                    logger.error(f"[Streamer] Bỏ qua câu vì không tìm thấy file audio: {audio_path}")
                    continue
                    
                duration = AVStreamer._get_audio_duration(audio_path)
                
                settings = {
                    "local_file": audio_path,
                    "is_local_file": True
                }
                create_input(scene_name, media_source_name, "ffmpeg_source", settings)
                set_media_file(media_source_name, audio_path)
                
                wrapped_sentence = SubtitleStreamer._wrap_text(sentence, max_words=12)
                set_text(text_source_name, wrapped_sentence)
                
                _trigger_media_action(media_source_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")
                
                logger.info(f"[Streamer] Đang phát câu: {sentence[:30]}... ({duration:.2f}s)")
                
                await asyncio.sleep(duration + 0.5)
                
                # Xóa file sau khi phát xong
                try:
                    os.remove(audio_path)
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"[Streamer] Lỗi trong quá trình stream: {e}")
                await asyncio.sleep(1)

    @staticmethod
    async def start_streaming(
        scene_name: str, 
        text_source_name: str, 
        media_source_name: str, 
        full_text: str,
        ref_audio_path: str = None
    ):
        """
        Hàm mồi để thiết lập Redis và khởi chạy 3 luồng (Worker Tasks) ngầm.
        """
        logger.info(f"Khởi chạy hệ thống Continuous AV Streaming cho {scene_name}...")
        
        redis = await get_redis()
        text_queue_key = AVStreamer.REDIS_TEXT_QUEUE.format(scene=scene_name)
        ready_queue_key = AVStreamer.REDIS_READY_QUEUE.format(scene=scene_name)
        status_key = AVStreamer.REDIS_STATUS.format(scene=scene_name)
        
        # 1. Đánh dấu trạng thái đang chạy
        await redis.set(status_key, "running")
        
        # 2. Xóa các queue cũ (nếu có) để không bị tồn đọng rác từ phiên trước
        await redis.delete(text_queue_key, ready_queue_key)
        
        # 3. Chèn đoạn text mồi ban đầu
        if full_text:
            clean_text = re.sub(r'\n+', ' ', full_text).strip()
            raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
            sentences = [s.strip() for s in raw_sentences if s.strip()]
            if sentences:
                await redis.rpush(text_queue_key, *sentences)
                logger.info(f"Đã nạp {len(sentences)} câu từ đoạn text ban đầu vào Queue.")
        
        # Khởi chạy 3 tasks background độc lập (không await block ở đây)
        loop = asyncio.get_running_loop()
        loop.create_task(AVStreamer._auto_generator_task(scene_name))
        loop.create_task(AVStreamer._prefetcher_task(scene_name, ref_audio_path))
        loop.create_task(AVStreamer._streamer_task(scene_name, text_source_name, media_source_name))
        
        logger.info("Hoàn tất khởi tạo luồng Stream Liên Tục!")
        
    @staticmethod
    async def stop_streaming(scene_name: str):
        """
        Ra lệnh dừng luồng AV Streaming bằng cách thay đổi trạng thái trong Redis.
        """
        redis = await get_redis()
        status_key = AVStreamer.REDIS_STATUS.format(scene=scene_name)
        await redis.set(status_key, "stopped")
        logger.info(f"Đã phát lệnh dừng luồng Stream cho cảnh {scene_name}.")

