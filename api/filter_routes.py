# api/filter_routes.py
import json
from fastapi import APIRouter, HTTPException, Form
from obs.filter import create_filter, remove_filter, set_filter_enabled

router = APIRouter(prefix="/api/obs/filter", tags=["OBS Filters"])

@router.post("/create")
def api_create_filter(
    source_name: str = Form(...),
    filter_name: str = Form(...),
    filter_kind: str = Form(..., description="'chroma_key_filter_v2' cho phông xanh, 'color_filter_v2' đổi màu"),
    filter_settings_json: str = Form("{}", description="JSON string thông số, ví dụ {\"opacity\": 0.5}")
):
    try:
        settings = json.loads(filter_settings_json)
    except:
        raise HTTPException(status_code=400, detail="filter_settings_json không đúng định dạng JSON")
        
    if not create_filter(source_name, filter_name, filter_kind, settings):
        raise HTTPException(status_code=400, detail="Không thể tạo Filter")
    return {"message": "Tạo Filter thành công!"}

@router.post("/remove")
def api_remove_filter(source_name: str = Form(...), filter_name: str = Form(...)):
    if not remove_filter(source_name, filter_name):
        raise HTTPException(status_code=400, detail="Không thể xóa Filter")
    return {"message": "Xóa Filter thành công!"}

@router.post("/toggle")
def api_toggle_filter(source_name: str = Form(...), filter_name: str = Form(...), enabled: bool = Form(...)):
    if not set_filter_enabled(source_name, filter_name, enabled):
        raise HTTPException(status_code=400, detail="Không thể Bật/Tắt Filter")
    return {"message": "Bật/Tắt Filter thành công!"}
