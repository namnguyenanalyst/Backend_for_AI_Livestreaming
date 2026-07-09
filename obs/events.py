# obs/events.py
import json
import redis
from core.config import REDIS_URL
from core.logger import get_logger
from obs.controller import obs_client

logger = get_logger("OBS_Events")

# Dùng Redis Client đồng bộ (sync) riêng cho background thread của OBS 
# để tránh xung đột với asyncio của FastAPI
try:
    sync_redis = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Lỗi kết nối Sync Redis cho OBS Events: {e}")
    sync_redis = None

def on_event(message):
    """Callback này sẽ được chạy ngầm mỗi khi OBS có sự kiện"""
    # obs-websocket-py bọc event trong biến 'name' và data trong 'datain'
    event_name = getattr(message, 'name', 'UnknownEvent')
    event_data = getattr(message, 'datain', {})
    
    logger.info(f"OBS vừa gửi Event: {event_name}")
    
    if sync_redis:
        try:
            # Bắn sự kiện lên Redis Event Bus để các module khác nhận được
            sync_redis.publish("obs_events", json.dumps({
                "event": event_name,
                "data": event_data
            }))
        except Exception as e:
            logger.error(f"Lỗi khi publish OBS event lên Redis: {e}")

def register_events():
    """Đăng ký các sự kiện muốn lắng nghe từ OBS"""
    if not obs_client.ws:
        logger.error("Chưa kết nối OBS, không thể đăng ký Event Listener.")
        return
        
    from obswebsocket import events
    
    try:
        # Đăng ký các sự kiện quan trọng
        obs_client.ws.register(on_event, events.CurrentProgramSceneChanged) # Khi chuyển cảnh
        obs_client.ws.register(on_event, events.StreamStateChanged)         # Khi bật/tắt stream
        obs_client.ws.register(on_event, events.RecordStateChanged)         # Khi bật/tắt record
        obs_client.ws.register(on_event, events.InputVolumeChanged)         # Khi đổi âm lượng
        
        logger.info("Đã đăng ký lắng nghe sự kiện từ OBS thành công.")
    except Exception as e:
        logger.error(f"Lỗi khi đăng ký sự kiện OBS: {e}")
