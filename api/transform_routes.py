# api/transform_routes.py
import json
from fastapi import APIRouter, HTTPException, Form
from obs.transform import set_transform, set_item_index

router = APIRouter(prefix="/api/obs/transform", tags=["OBS Transform"])

@router.post("/set")
def api_set_transform(
    scene_name: str = Form(...),
    source_name: str = Form(...),
    transform_json: str = Form(..., description="JSON string: {\"positionX\": 100, \"positionY\": 100, \"scaleX\": 0.5, \"scaleY\": 0.5}")
):
    try:
        transform_data = json.loads(transform_json)
    except:
        raise HTTPException(status_code=400, detail="transform_json không đúng định dạng JSON")
        
    if not set_transform(scene_name, source_name, transform_data):
        raise HTTPException(status_code=400, detail="Không thể cập nhật Tọa độ/Kích thước")
        
    return {"message": "Cập nhật Tọa độ/Kích thước thành công!"}

@router.post("/set_index")
def api_set_index(
    scene_name: str = Form(...),
    source_name: str = Form(...),
    index: int = Form(..., description="Vị trí Z-Index (0 là dưới cùng, số càng to càng nổi lên trên)")
):
    if not set_item_index(scene_name, source_name, index):
        raise HTTPException(status_code=400, detail="Không thể thay đổi vị trí lớp (Z-Index)")
    return {"message": f"Đã chuyển '{source_name}' tới lớp thứ {index} thành công!"}
