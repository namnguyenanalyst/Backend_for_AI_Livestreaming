# api/audio_routes.py
from fastapi import APIRouter, HTTPException, Form
from obs.audio import set_input_mute, set_input_volume

router = APIRouter(prefix="/api/obs/audio", tags=["OBS Audio"])

@router.post("/mute")
def api_set_mute(source_name: str = Form(...), is_muted: bool = Form(..., description="True để tắt tiếng, False để bật tiếng")):
    if not set_input_mute(source_name, is_muted):
        raise HTTPException(status_code=400, detail="Lỗi Mute Nguồn Âm Thanh")
    return {"message": f"Đã {'tắt' if is_muted else 'bật'} tiếng của '{source_name}'"}

@router.post("/volume")
def api_set_volume(source_name: str = Form(...), volume_db: float = Form(..., description="Ví dụ: 0.0 là mức gốc, -10.5 là giảm nhỏ đi")):
    if not set_input_volume(source_name, volume_db):
        raise HTTPException(status_code=400, detail="Lỗi chỉnh Volume")
    return {"message": f"Đã chỉnh Volume '{source_name}' thành {volume_db} dB"}
