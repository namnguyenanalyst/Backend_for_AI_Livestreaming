# obs/transform.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Transform")

def get_scene_item_id(scene_name: str, source_name: str):
    """Hàm phụ trợ lấy ID của một Source nằm trong một Scene"""
    try:
        response = obs_client.ws.call(requests.GetSceneItemId(
            sceneName=scene_name, 
            sourceName=source_name
        ))
        return response.getSceneItemId()
    except exceptions.Error:
        return None

def set_transform(scene_name: str, source_name: str, transform_data: dict):
    """Di chuyển, thu phóng, xoay Source"""
    if not obs_client.ws: 
        return False
        
    item_id = get_scene_item_id(scene_name, source_name)
    if not item_id:
        logger.error(f"Không tìm thấy source '{source_name}' trong scene '{scene_name}'")
        return False
        
    try:
        obs_client.ws.call(requests.SetSceneItemTransform(
            sceneName=scene_name,
            sceneItemId=item_id,
            sceneItemTransform=transform_data
        ))
        logger.info(f"Đã cập nhật Transform cho '{source_name}'")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi set transform: {e}")
        return False

def set_item_index(scene_name: str, source_name: str, target_index: int):
    """Thay đổi vị trí Z-Index (sắp xếp lớp) của Nguồn"""
    if not obs_client.ws: 
        return False
        
    item_id = get_scene_item_id(scene_name, source_name)
    if not item_id:
        logger.error(f"Không tìm thấy source '{source_name}' trong scene '{scene_name}'")
        return False
        
    try:
        obs_client.ws.call(requests.SetSceneItemIndex(
            sceneName=scene_name,
            sceneItemId=item_id,
            sceneItemIndex=target_index
        ))
        logger.info(f"Đã đưa '{source_name}' tới index {target_index}")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi sắp xếp lớp: {e}")
        return False
