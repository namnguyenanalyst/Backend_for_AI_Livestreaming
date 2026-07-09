# obs/filter.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Filter")

def create_filter(source_name: str, filter_name: str, filter_kind: str, filter_settings: dict = None):
    """Thêm một Filter vào Source"""
    if filter_settings is None: 
        filter_settings = {}
    if not obs_client.ws: 
        return False
    try:
        obs_client.ws.call(requests.CreateSourceFilter(
            sourceName=source_name, 
            filterName=filter_name, 
            filterKind=filter_kind, 
            filterSettings=filter_settings
        ))
        logger.info(f"Đã tạo filter '{filter_name}' cho '{source_name}'")
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi tạo filter: {e}")
        return False

def remove_filter(source_name: str, filter_name: str):
    """Xóa một Filter khỏi Source"""
    if not obs_client.ws: 
        return False
    try:
        obs_client.ws.call(requests.RemoveSourceFilter(
            sourceName=source_name, 
            filterName=filter_name
        ))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi xóa filter: {e}")
        return False

def set_filter_enabled(source_name: str, filter_name: str, enabled: bool):
    """Bật/tắt một Filter"""
    if not obs_client.ws: 
        return False
    try:
        obs_client.ws.call(requests.SetSourceFilterEnabled(
            sourceName=source_name, 
            filterName=filter_name, 
            filterEnabled=enabled
        ))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi bật/tắt filter: {e}")
        return False
