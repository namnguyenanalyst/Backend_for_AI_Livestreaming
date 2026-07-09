# obs/audio.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions
logger = get_logger("OBS_Audio")
def set_input_mute(input_name: str, is_muted: bool):
    """Bật hoặc tắt tiếng (Mute) một nguồn âm thanh"""
    if not obs_client.ws:
        return False
    try:
        obs_client.ws.call(requests.SetInputMute(
            inputName=input_name,
            inputMuted=is_muted
        ))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi khi Mute '{input_name}': {e}")
        return False

def set_input_volume(input_name: str, volume_db: float):
    """Chỉnh âm lượng theo dB (Ví dụ: 0.0 là mức gốc, -10.5 là giảm đi)"""
    if not obs_client.ws:
        return False
    try:
        obs_client.ws.call(requests.SetInputVolume(
            inputName=input_name,
            inputVolumeDb=volume_db
        ))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi chỉnh âm lượng '{input_name}': {e}")
        return False