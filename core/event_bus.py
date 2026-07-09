# core/event_bus.py
import json
import redis.asyncio as redis
from core.config import REDIS_URL
from core.logger import get_logger
logger = get_logger("EventBus")

class EventBus:
    def __init__(self):
        # Kết nối tới Redis, tự động chuyển đổi byte sang string (decode_responses=True)
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    async def publish(self, channel: str, message: dict):
        """Gửi một sự kiện (event) lên một kênh (channel)"""
        try:
            msg_str = json.dumps(message)
            await self.redis.publish(channel, msg_str)
            logger.debug(f"Đã đẩy event tới [{channel}]: {message}")
        except Exception as e:
            logger.error(f"Lỗi khi đẩy event tới {channel}: {e}")
    
    async def subscribe(self, channel: str):
        """Đăng ký lắng nghe sự kiện trên một kênh (channel)"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Bắt đầu lắng nghe sự kiện trên kênh: [{channel}]")
            return pubsub
        except Exception as e:
            logger.error(f"Lỗi khi subscribe {channel}: {e}")
            return None
# Tạo instance duy nhất để dùng chung toàn hệ thống
event_bus = EventBus()