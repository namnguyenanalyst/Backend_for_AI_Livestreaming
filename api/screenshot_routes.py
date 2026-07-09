# api/screenshot_routes.py
from fastapi import APIRouter, HTTPException
from obs.screenshot import get_screenshot

router = APIRouter(prefix="/api/obs/screenshot", tags=["OBS Screenshot"])

@router.get("/{source_name}")
def api_get_screenshot(source_name: str):
    """Gọi API này sẽ trả về Data URI chứa ảnh tĩnh của Source/Scene"""
    data = get_screenshot(source_name)
    if not data:
        raise HTTPException(status_code=400, detail="Không thể chụp ảnh hoặc Source không tồn tại")
    return {"image_data": data}
