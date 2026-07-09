# obs/screenshot.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Screenshot")

def get_screenshot(source_name: str):
    """Chụp ảnh màn hình một Nguồn hoặc Phân cảnh bất kỳ và trả về chuỗi Base64"""
    if not obs_client.ws: return None
    try:
        response = obs_client.ws.call(requests.GetSourceScreenshot(
            sourceName=source_name, 
            imageFormat="png", 
            imageWidth=1280, 
            imageHeight=720
        ))
        # Chuỗi này có dạng data:image/png;base64,....
        return response.getImageData() 
    except exceptions.Error as e:
        logger.error(f"Lỗi chụp ảnh '{source_name}': {e}")
        return None
