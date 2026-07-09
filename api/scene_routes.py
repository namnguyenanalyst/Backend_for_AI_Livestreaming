from fastapi import APIRouter, HTTPException, Form
from obs.scene import create_scene, set_current_scene, get_current_scene, get_scene_items, get_scene_list

router = APIRouter(prefix="/api/obs/scene", tags=["OBS Scene"])

@router.post("/create")
def api_create_scene(scene_name: str = Form(...)):
    success = create_scene(scene_name)
    if not success:
        raise HTTPException(status_code=400, detail="Lỗi khi tạo Scene")
    return {"message": f"Tạo Scene '{scene_name}' thành công!"}

@router.post("/change")
def api_change_scene(scene_name: str = Form(...)):
    success = set_current_scene(scene_name)
    if not success:
        raise HTTPException(status_code=400, detail="Lỗi khi chuyển Scene")
    return {"message": f"Đã chuyển sang Scene '{scene_name}'"}

@router.get("/info")
def api_get_scene_info():
    current_scene = get_current_scene()
    if not current_scene:
        raise HTTPException(status_code=400, detail="Không lấy được Scene hiện tại")
    
    sources = get_scene_items(current_scene)
    return {
        "current_scene": current_scene,
        "sources": sources
    }

@router.get("/list")
def api_get_scenes():
    scenes = get_scene_list()
    return {"scenes": scenes}
