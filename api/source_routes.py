import os
import shutil
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from obs.source import create_input, set_source_visibility, set_text, play_media, pause_media, stop_media

router = APIRouter(prefix="/api/obs/source", tags=["OBS Source"])

@router.post("/create")
async def api_create_source(
    scene_name: str = Form(...), 
    input_name: str = Form(...), 
    input_kind: str = Form(...),
    media_file: Optional[UploadFile] = File(None, description="Tùy chọn: Upload file nếu là video/ảnh"),
    settings_json: Optional[str] = Form(None, description="Tùy chọn: JSON cấu hình nâng cao"),
    color_rgb: Optional[str] = Form(None, description="Tùy chọn: Nhập mã RGB (VD: '255,0,0') để set màu")
):
    settings = {}
    file_msg = ""
    
    # 1. Parse settings JSON nếu có
    if settings_json:
        try:
            settings.update(json.loads(settings_json))
        except Exception:
            raise HTTPException(status_code=400, detail="settings_json không hợp lệ")

    # 1.5. Nếu có nhập màu RGB (R,G,B) -> Tự động chuyển đổi sang 32-bit của OBS
    if color_rgb:
        try:
            parts = color_rgb.replace(" ", "").split(",")
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            # Công thức mã màu của OBS: AABBGGRR (Alpha-Blue-Green-Red)
            obs_color_int = (255 << 24) | (b << 16) | (g << 8) | r
            settings["color"] = obs_color_int
        except Exception:
            raise HTTPException(status_code=400, detail="Định dạng RGB sai. Ví dụ đúng: '255,0,0'")

    # 2. Nếu có đính kèm file thì tự động gán đường dẫn vào settings
    if media_file is not None and media_file.filename:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", media_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(media_file.file, buffer)
        abs_path = os.path.abspath(file_path)
        settings.update({
            "local_file": abs_path, 
            "file": abs_path,
            "playlist": [{"value": abs_path, "selected": False, "hidden": False}]
        })
        file_msg = f" (Đã đính kèm file: {media_file.filename})"

    # Tạo nguồn trên OBS
    success = create_input(scene_name, input_name, input_kind, settings)
    if not success:
        raise HTTPException(status_code=400, detail="Không thể tạo Source")
        
    return {"message": f"Tạo Source '{input_name}' thành công!{file_msg}"}

@router.post("/text/update")
def api_update_text(source_name: str = Form(...), text_content: str = Form(...)):
    success = set_text(source_name, text_content)
    if not success:
        raise HTTPException(status_code=400, detail="Lỗi update Text")
    return {"message": "Cập nhật Text thành công!"}

@router.post("/visibility")
def api_set_visibility(scene_name: str = Form(...), source_name: str = Form(...), is_visible: bool = Form(...)):
    if not set_source_visibility(scene_name, source_name, is_visible):
        raise HTTPException(status_code=400, detail="Lỗi đổi Visibility")
    return {"message": f"Đã {'hiển thị' if is_visible else 'ẩn'} '{source_name}'"}

@router.post("/media/play")
def api_play_media(source_name: str = Form(...)):
    if not play_media(source_name):
        raise HTTPException(status_code=400, detail="Lỗi Play Media")
    return {"message": f"Đã Play '{source_name}'"}

@router.post("/media/pause")
def api_pause_media(source_name: str = Form(...)):
    if not pause_media(source_name):
        raise HTTPException(status_code=400, detail="Lỗi Pause Media")
    return {"message": f"Đã Pause '{source_name}'"}

@router.post("/media/stop")
def api_stop_media(source_name: str = Form(...)):
    if not stop_media(source_name):
        raise HTTPException(status_code=400, detail="Lỗi Stop Media")
    return {"message": f"Đã Stop '{source_name}'"}
