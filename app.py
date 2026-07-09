# app.py
from fastapi import FastAPI
from obs.controller import obs_client
from core.logger import get_logger
from core.event_bus import event_bus
from api.scene_routes import router as scene_router
from api.source_routes import router as source_router
from api.filter_routes import router as filter_router
from api.transform_routes import router as transform_router
from api.transition_routes import router as transition_router
from api.output_routes import router as output_router
from api.screenshot_routes import router as screenshot_router
from api.studio_routes import router as studio_router
from api.audio_routes import router as audio_router
from api.llm_routes import router as llm_router
from api.workflow_routes import router as workflow_router
from api.webhook_routes import router as webhook_router

logger = get_logger("FastAPI_App")
app = FastAPI(title="AI Livestream Backend")

# Đăng ký các API của OBS vào app

app.include_router(scene_router)
app.include_router(source_router)
app.include_router(filter_router)
app.include_router(transform_router)
app.include_router(transition_router)
app.include_router(output_router)
app.include_router(screenshot_router)
app.include_router(studio_router)
app.include_router(audio_router)
app.include_router(llm_router)
app.include_router(workflow_router)
app.include_router(webhook_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Đang khởi động Backend...")
    # Thử kết nối với OBS
    success = obs_client.connect()
    if success:
        # Nếu kết nối thành công, lấy version của OBS ra xem thử
        obs_client.get_version()

        # Gọi module lắng nghe sự kiện
        from obs.events import register_events
        register_events()

        # TEST: Bắn thử một event lên Redis
        await event_bus.publish("system_events", {"type": "STARTUP", "status": "OBS Connected"})
    else:
        logger.error("Không thể kết nối OBS. Vui lòng kiểm tra lại OBS Studio đã bật WebSocket chưa.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Đang tắt Backend...")
    obs_client.disconnect()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Livestream Backend đang chạy!"}
