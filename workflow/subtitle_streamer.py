import asyncio
import re
from core.logger import get_logger
from obs.source import set_text

logger = get_logger("SubtitleStreamer")

class SubtitleStreamer:
    """
    Trình quản lý tiến trình chạy phụ đề trên OBS.
    """
    
    @staticmethod
    def _wrap_text(text: str, max_words: int = 12) -> str:
        """
        Chia một câu thành nhiều dòng, mỗi dòng tối đa `max_words` từ.
        Bảo toàn các ngắt dòng vật lý có sẵn trong văn bản.
        """
        paragraphs = text.split('\n')
        lines = []
        for p in paragraphs:
            words = p.split()
            for i in range(0, len(words), max_words):
                lines.append(" ".join(words[i:i+max_words]))
        return "\n".join(lines)

    
    @staticmethod
    async def start_streaming(source_name: str, full_text: str, delay_seconds: float = 4.0):
        """
        Chạy ngầm (Background Task) để cắt văn bản thành từng câu và đẩy lên OBS lần lượt.
        """
        logger.info(f"Bắt đầu chạy phụ đề cho source '{source_name}'.")
        
        # Tiền xử lý: Biến chuỗi "\n" thành ngắt dòng vật lý thực sự và giữ nguyên
        full_text = full_text.replace("\\n", "\n")
        clean_text = full_text.strip()
        
        # Tách câu bằng Regex (dựa vào dấu ., ?, ! theo sau là khoảng trắng)
        # Bao gồm cả dấu trong kết quả cắt
        raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
        
        # Lọc bỏ các câu rỗng
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        if not sentences:
            logger.warning("Không tìm thấy câu nào hợp lệ để chạy phụ đề.")
            return

        for idx, sentence in enumerate(sentences):
            try:
                # Tự động xuống dòng nếu câu quá dài (mặc định 12 từ/dòng)
                wrapped_sentence = SubtitleStreamer._wrap_text(sentence, max_words=12)
                
                # Đẩy từng câu lên OBS
                success = set_text(source_name, wrapped_sentence)
                if not success:
                    logger.error(f"Lỗi khi đẩy câu lên OBS: {sentence}")
                else:
                    logger.debug(f"Đang hiển thị ({idx+1}/{len(sentences)}): {sentence}")
                
                # Chờ vài giây trước khi hiện câu tiếp theo
                await asyncio.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Lỗi trong quá trình stream phụ đề: {e}")
                break
                
        # Xóa chữ trên màn hình sau khi kết thúc
        set_text(source_name, "")
        logger.info(f"Hoàn thành trình chiếu phụ đề cho '{source_name}'. Đã dọn dẹp màn hình.")
