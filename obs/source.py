# obs/source.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Source")

def create_input(scene_name: str, input_name: str, input_kind: str, input_settings: dict = None):
    """
    Tạo một nguồn mới và gán vào phân cảnh (Scene).
    - input_kind (Linux): 'text_ft2_source_v2', 'image_source', 'vlc_source', 'xshm_input'...
    - input_settings: cấu hình đặc thù (ví dụ: đường dẫn file).
    """
    if not obs_client.ws:
        return False
    
    if input_settings is None:
        input_settings = {}
        
    try:
        obs_client.ws.call(requests.CreateInput(
            sceneName=scene_name,
            inputName=input_name,
            inputKind=input_kind,
            inputSettings=input_settings,
            sceneItemEnabled=True
        ))
        logger.info(f"Đã tạo nguồn '{input_name}' loại '{input_kind}' trong cảnh '{scene_name}'")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi tạo nguồn '{input_name}': {e}")
        return False

def remove_input(input_name: str):
    """Xóa hoàn toàn một nguồn khỏi OBS"""
    if not obs_client.ws:
        return False
    
    try:
        obs_client.ws.call(requests.RemoveInput(inputName=input_name))
        logger.info(f"Đã xóa nguồn: {input_name}")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi xóa nguồn '{input_name}': {e}")
        return False

def _get_scene_item_id(scene_name: str, source_name: str):
    """Hàm nội bộ để lấy ID của một nguồn nằm trong một cảnh"""
    try:
        response = obs_client.ws.call(requests.GetSceneItemId(
            sceneName=scene_name, 
            sourceName=source_name
        ))
        return response.getSceneItemId()
    except exceptions.Error:
        return None

def set_source_visibility(scene_name: str, source_name: str, is_visible: bool):
    """Bật/tắt hiển thị (biểu tượng con mắt) của một nguồn"""
    if not obs_client.ws:
        return False
    
    item_id = _get_scene_item_id(scene_name, source_name)
    if item_id is None:
        logger.warning(f"Không tìm thấy '{source_name}' trong '{scene_name}'")
        return False
        
    try:
        obs_client.ws.call(requests.SetSceneItemEnabled(
            sceneName=scene_name,
            sceneItemId=item_id,
            sceneItemEnabled=is_visible
        ))
        logger.info(f"Đã {'bật' if is_visible else 'tắt'} hiển thị của '{source_name}'")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi đổi visibility: {e}")
        return False

def set_text(input_name: str, text_content: str):
    """Cập nhật nội dung chữ của một Text Source (dùng cho Subtitle/LLM)"""
    if not obs_client.ws:
        return False
    
    try:
        obs_client.ws.call(requests.SetInputSettings(
            inputName=input_name,
            inputSettings={"text": text_content},
            overlay=True  # Ghi đè chỉ mục text, giữ nguyên các cài đặt khác như font, màu...
        ))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi khi set text cho '{input_name}': {e}")
        return False

def set_media_file(input_name: str, file_path: str):
    """Thay đổi đường dẫn file của một Image hoặc VLC/Media Source"""
    if not obs_client.ws:
        return False
    try:
        obs_client.ws.call(requests.SetInputSettings(
            inputName=input_name,
            inputSettings={"local_file": file_path, "file": file_path, "is_local_file": True},
            overlay=True
        ))
        logger.info(f"Đã cập nhật file cho '{input_name}': {file_path}")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi đổi file media: {e}")
        return False

def _trigger_media_action(input_name: str, action: str):
    if not obs_client.ws:
        return False
    try:
        obs_client.ws.call(requests.TriggerMediaInputAction(
            inputName=input_name,
            mediaAction=action
        ))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi media action '{action}' trên '{input_name}': {e}")
        return False

def play_media(input_name: str):
    return _trigger_media_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY")
def pause_media(input_name: str):
    return _trigger_media_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE")
def stop_media(input_name: str):
    return _trigger_media_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP")
