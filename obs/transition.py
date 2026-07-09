# obs/transition.py
from obs.controller import obs_client
from core.logger import get_logger
from obswebsocket import requests, exceptions

logger = get_logger("OBS_Transition")

def get_transition_list():
    if not obs_client.ws: return []
    try:
        response = obs_client.ws.call(requests.GetSceneTransitionList())
        return [t['transitionName'] for t in response.getTransitions()]
    except exceptions.Error as e:
        logger.error(f"Lỗi lấy danh sách transition: {e}")
        return []

def set_current_transition(transition_name: str):
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.SetCurrentSceneTransition(transitionName=transition_name))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi set transition: {e}")
        return False

def set_transition_duration(duration_ms: int):
    if not obs_client.ws: return False
    try:
        obs_client.ws.call(requests.SetCurrentSceneTransitionDuration(transitionDuration=duration_ms))
        return True
    except exceptions.Error as e:
        logger.error(f"Lỗi set thời gian transition: {e}")
        return False
