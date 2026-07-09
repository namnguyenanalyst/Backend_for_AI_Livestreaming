# obs/output.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Output")

def toggle_virtual_cam():
    if not obs_client.ws: return False
    try:
        response = obs_client.ws.call(requests.ToggleVirtualCam())
        return response.getOutputActive()
    except exceptions.Error as e:
        logger.error(f"Lỗi toggle virtual cam: {e}")
        return False

def get_stream_status():
    if not obs_client.ws: return False
    try:
        response = obs_client.ws.call(requests.GetStreamStatus())
        return response.getOutputActive()
    except exceptions.Error as e:
        logger.error(f"Lỗi lấy trạng thái stream: {e}")
        return False

def start_stream():
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.StartStream())
        return True
    except exceptions.Error: return False

def stop_stream():
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.StopStream())
        return True
    except exceptions.Error: return False

def start_record():
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.StartRecord())
        return True
    except exceptions.Error: return False

def stop_record():
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.StopRecord())
        return True
    except exceptions.Error: return False
