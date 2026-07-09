# api/studio_routes.py
from fastapi import APIRouter, HTTPException, Form
from obs.studio import (
    set_studio_mode_enabled,
    get_studio_mode_enabled,
    set_current_preview_scene,
    get_current_preview_scene,
    trigger_studio_mode_transition
)

router = APIRouter(prefix="/api/obs/studio", tags=["OBS Studio Mode"])

@router.post("/toggle")
def api_toggle_studio_mode(enabled: bool = Form(..., description="True để bật, False để tắt")):
    if not set_studio_mode_enabled(enabled):
        raise HTTPException(status_code=400, detail="Không thể thay đổi trạng thái Studio Mode")
    return {"message": f"Đã {'bật' if enabled else 'tắt'} Studio Mode"}

@router.get("/status")
def api_get_studio_mode_status():
    return {"studio_mode_enabled": get_studio_mode_enabled()}

@router.post("/preview/set")
def api_set_preview_scene(scene_name: str = Form(...)):
    if not set_current_preview_scene(scene_name):
        raise HTTPException(status_code=400, detail="Không thể đặt Preview Scene")
    return {"message": f"Đã đưa '{scene_name}' vào màn hình Preview"}

@router.get("/preview/get")
def api_get_preview_scene():
    scene = get_current_preview_scene()
    if not scene:
        raise HTTPException(status_code=400, detail="Không thể lấy Preview Scene (Có thể Studio Mode đang tắt)")
    return {"preview_scene": scene}

@router.post("/transition")
def api_trigger_transition():
    if not trigger_studio_mode_transition():
        raise HTTPException(status_code=400, detail="Lỗi thực hiện Transition")
    return {"message": "Đã thực hiện Transition chuyển lên màn hình Live!"}
