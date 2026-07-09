from obswebsocket import obsws, requests, exceptions
from core.config import OBS_HOST, OBS_PASSWORD, OBS_PORT
from core.logger import get_logger

logger = get_logger("OBSController")

class OBSController:
    def __init__(self):
        self.host = OBS_HOST
        self.password = OBS_PASSWORD
        self.port = OBS_PORT
        self.ws = None
    
    def connect(self):
        """Kết nối tới OBS WebSocket"""
        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            logger.info(f"Đã kết nối thành công tới OBS WebSocket tại {self.host}:{self.port}")
            return True
        except exceptions.ConnectionFailure as e:
            logger.error(f"Lỗi kết nối OBS: {e}")
            self.ws = None
            return False
    
    def disconnect(self):
        """Ngắt kết nối OBS"""
        if self.ws:
            self.ws.disconnect()
            self.ws = None
            logger.info("Đã ngắt kết nối OBS.")
    
    def get_version(self):
        """Lấy phiên bản OBS để test"""
        if not self.ws:
            logger.error("Chưa kết nối OBS.")
            return None
        
        try:
            response = self.ws.call(requests.GetVersion())
            logger.info(f"OBS Version: {response.getObsVersion()}")
            return response.datain
        except Exception as e:
            logger.error(f"Lỗi khi lấy version: {e}")
            return None
# Tạo một instance duy nhất (Singleton pattern cơ bản) để các file khác import dùng chung
obs_client = OBSController()
        

