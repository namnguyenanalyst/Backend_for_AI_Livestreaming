from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Scene")

def create_scene(scene_name: str):
    """Tạo một Phân cảnh (Scene) hoàn toàn mới"""
    if not obs_client.ws:
        return False
    try:
        obs_client.ws.call(requests.CreateScene(sceneName=scene_name))
        logger.info(f"Đã tạo phân cảnh mới: {scene_name}")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi tạo scene '{scene_name}': {e}")
        return False

def remove_scene(scene_name: str):
    """Xóa một Phân cảnh"""
    if not obs_client.ws:
        return False
    try:
        obs_client.ws.call(requests.RemoveScene(sceneName=scene_name))
        logger.info(f"Đã xóa phân cảnh: {scene_name}")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi xóa scene '{scene_name}': {e}")
        return False

def get_scene_list():
    """Lấy danh sách các Phân cảnh (Scenes) hiện có trong OBS"""
    if not obs_client.ws:
        logger.error("Chưa kết nối tới OBS")
        return []
    try:
        response = obs_client.ws.call(requests.GetSceneList())
        scenes = response.getScenes()
        # scenes là một list các dictionary
        return [scene['sceneName'] for scene in scenes]
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách scene: {e}")
        return []

def get_current_scene():
    """Lấy tên Phân cảnh đang được hiển thị"""
    if not obs_client.ws:
        return None
    
    try:
        response = obs_client.ws.call(requests.GetCurrentProgramScene())
        return response.getSceneName()
    except Exception as e:
        logger.error(f"Lỗi khi lấy scene hiện tại: {e}")
        return None

def set_current_scene(scene_name: str):
    """Chuyển sang một Phân cảnh khác"""
    if not obs_client.ws:
        return False
    
    try:
        obs_client.ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
        logger.info(f"Đã chuyển sang phân cảnh: {scene_name}")
        return True
    except exceptions.Error as e:
        logger.error(f"Không thể chuyển scene (Có thể scene '{scene_name}' không tồn tại): {e}")
        return False

def get_scene_items(scene_name: str):
    """Lấy danh sách các Nguồn (Sources) đang có trong một Phân cảnh"""
    if not obs_client.ws:
        return []
    try:
        response = obs_client.ws.call(requests.GetSceneItemList(sceneName=scene_name))
        items = response.getSceneItems()
        # Lọc ra tên của các Source
        return [item['sourceName'] for item in items]
    except exceptions.Error as e:
        logger.error(f"Lỗi khi lấy danh sách source của scene '{scene_name}': {e}")
        return []