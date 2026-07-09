# api/transition_routes.py
from fastapi import APIRouter, HTTPException, Form
from obs.transition import get_transition_list, set_current_transition, set_transition_duration

router = APIRouter(prefix="/api/obs/transition", tags=["OBS Transitions"])

@router.get("/list")
def api_get_transitions():
    return {"transitions": get_transition_list()}

@router.post("/set")
def api_set_transition(transition_name: str = Form(...)):
    if not set_current_transition(transition_name):
        raise HTTPException(status_code=400, detail="Không thể đổi Transition")
    return {"message": f"Đổi thành {transition_name} thành công!"}

@router.post("/duration")
def api_set_transition_duration(duration_ms: int = Form(...)):
    if not set_transition_duration(duration_ms):
        raise HTTPException(status_code=400, detail="Không thể đổi tốc độ Transition")
    return {"message": "Đổi tốc độ thành công!"}
