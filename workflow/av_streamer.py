import asyncio
import re
import os
from mutagen.wave import WAVE
from core.logger import get_logger
from obs.source import set_text, create_input, play_media
from clients.omnivoice_client import OmniVoiceClient
from workflow.subtitle_streamer import SubtitleStreamer

logger = get_logger("AVStreamer")

class AVStreamer:
    """
    Trình quản lý tiến trình Đồng bộ Phụ đề và Giọng nói (Audio-Visual).
    """
    
    @staticmethod
    def _get_audio_duration(file_path: str) -> float:
        try:
            audio = WAVE(file_path)
            return audio.info.length
        except Exception as e:
            logger.error(f"Không thể đọc độ dài audio {file_path}: {e}")
            return 3.0 # Trả về mặc định 3 giây nếu lỗi
            
    @staticmethod
    async def start_streaming(
        scene_name: str, 
        text_source_name: str, 
        media_source_name: str, 
        full_text: str,
        ref_audio_path: str = None
    ):
        """
        Cắt văn bản, gọi AI sinh giọng nói, rồi đẩy chữ và âm thanh lên OBS đồng thời.
        """
        logger.info(f"Bắt đầu AV Streaming. Cảnh: {scene_name}, Text: {text_source_name}, Audio: {media_source_name}")
        
        clean_text = re.sub(r'\n+', ' ', full_text).strip()
        raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        if not sentences:
            logger.warning("Không có câu nào hợp lệ.")
            return

        for idx, sentence in enumerate(sentences):
            logger.info(f"Đang xử lý câu ({idx+1}/{len(sentences)}): {sentence[:30]}...")
            
            # 1. Gọi OmniVoice và ĐỢI (Chờ Webhook trả về)
            if ref_audio_path:
                audio_path = await OmniVoiceClient.generate_speech(sentence, ref_audio_path=ref_audio_path)
            else:
                audio_path = await OmniVoiceClient.generate_speech(sentence)
                
            if not audio_path or not os.path.exists(audio_path):
                logger.error(f"Bỏ qua câu này vì không lấy được Audio: {sentence}")
                continue
                
            # 2. Đo độ dài âm thanh
            duration = AVStreamer._get_audio_duration(audio_path)
            
            # 3. Nạp audio vào OBS (Tạo Media Source ẩn)
            settings = {
                "local_file": audio_path,
                "is_local_file": True
            }
            # Thử tạo mới (nếu chưa có)
            create_input(scene_name, media_source_name, "ffmpeg_source", settings)
            
            # BẮT BUỘC: Cập nhật đường dẫn file cho Source (vì nếu source đã tồn tại, create_input ở trên sẽ bị bỏ qua)
            from obs.source import set_media_file, _trigger_media_action
            set_media_file(media_source_name, audio_path)
            
            # 4. Bắn chữ lên OBS (Có tự động ngắt dòng 12 từ)
            wrapped_sentence = SubtitleStreamer._wrap_text(sentence, max_words=12)
            set_text(text_source_name, wrapped_sentence)
            
            # 5. Phát Audio (Dùng RESTART thay vì PLAY để chắc chắn nó phát lại từ đầu file mới)
            _trigger_media_action(media_source_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")

            # 6. Ngủ đông vòng lặp đúng bằng thời gian câu nói (cộng thêm 0.5s nghỉ ngơi)
            await asyncio.sleep(duration + 0.5)
            
            # Xóa file rác để tránh đầy ổ cứng
            try:
                os.remove(audio_path)
            except Exception:
                pass
                
        # Dọn dẹp màn hình khi xong
        set_text(text_source_name, "")
        logger.info("Hoàn tất tiến trình AV Streaming!")
