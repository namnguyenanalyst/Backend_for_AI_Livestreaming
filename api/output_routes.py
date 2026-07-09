# api/output_routes.py
from fastapi import APIRouter, HTTPException
from obs.output import toggle_virtual_cam, get_stream_status, start_stream, stop_stream, start_record, stop_record

router = APIRouter(prefix="/api/obs/output", tags=["OBS Outputs"])

@router.post("/virtual_cam/toggle")
def api_toggle_virtual_cam():
    active = toggle_virtual_cam()
    return {"virtual_cam_active": active}

@router.get("/stream/status")
def api_get_stream_status():
    return {"streaming": get_stream_status()}

@router.post("/stream/start")
def api_start_stream():
    if not start_stream(): raise HTTPException(status_code=400, detail="Lỗi bật Stream")
    return {"message": "Started Stream"}

@router.post("/stream/stop")
def api_stop_stream():
    if not stop_stream(): raise HTTPException(status_code=400, detail="Lỗi tắt Stream")
    return {"message": "Stopped Stream"}

@router.post("/record/start")
def api_start_record():
    if not start_record(): raise HTTPException(status_code=400, detail="Lỗi bật Record")
    return {"message": "Started Record"}

@router.post("/record/stop")
def api_stop_record():
    if not stop_record(): raise HTTPException(status_code=400, detail="Lỗi tắt Record")
    return {"message": "Stopped Record"}
