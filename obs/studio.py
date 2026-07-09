# obs/studio.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Studio")

def set_studio_mode_enabled(enabled: bool):
    """Bật/tắt chế độ Studio Mode (Màn hình đôi)"""
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.SetStudioModeEnabled(studioModeEnabled=enabled))
        logger.info(f"Đã {'bật' if enabled else 'tắt'} Studio Mode")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi toggle Studio Mode: {e}")
        return False

def get_studio_mode_enabled():
    """Kiểm tra xem chế độ Studio Mode có đang bật hay không"""
    if not obs_client.ws: return False
    try:
        response = obs_client.ws.call(requests.GetStudioModeEnabled())
        return response.getStudioModeEnabled()
    except exceptions.Error as e:
        logger.error(f"Lỗi lấy trạng thái Studio Mode: {e}")
        return False

def set_current_preview_scene(scene_name: str):
    """Đặt một Phân cảnh vào màn hình Preview (Bên trái) để chuẩn bị"""
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.SetCurrentPreviewScene(sceneName=scene_name))
        logger.info(f"Đã đặt '{scene_name}' vào màn hình Preview")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi set Preview Scene: {e}")
        return False

def get_current_preview_scene():
    """Lấy tên Phân cảnh đang chờ trên màn hình Preview"""
    if not obs_client.ws: return None
    try:
        response = obs_client.ws.call(requests.GetCurrentPreviewScene())
        return response.getSceneName()
    except exceptions.Error as e:
        logger.error(f"Lỗi lấy Preview Scene hiện tại: {e}")
        return None

def trigger_studio_mode_transition():
    """Kích hoạt nút chuyển cảnh, đẩy từ Preview (Trái) sang Program (Phải)"""
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.TriggerStudioModeTransition())
        logger.info("Đã kích hoạt Transition (Preview -> Program)")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi kích hoạt Transition: {e}")
        return False
