import redis.asyncio as redis
from core.config import REDIS_URL
from core.logger import get_logger

logger = get_logger("RedisClient")

# Biến global lưu instance Redis pool
_redis_pool = None

async def get_redis():
    """
    Trả về đối tượng kết nối tới Redis (singleton pattern dùng connection pool).
    """
    global _redis_pool
    if _redis_pool is None:
        logger.info(f"Khởi tạo kết nối Redis tới: {REDIS_URL}")
        _redis_pool = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_pool
