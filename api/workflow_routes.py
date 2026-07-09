from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, File, UploadFile
import os
import shutil
from workflow.subtitle_streamer import SubtitleStreamer

router = APIRouter(prefix="/api/workflow", tags=["Workflows"])

@router.post("/subtitle/start")
def start_subtitle_stream(
    background_tasks: BackgroundTasks,
    source_name: str = Form(..., description="Tên nguồn Text trong OBS (VD: Text - MC)"),
    text_content: str = Form(..., description="Đoạn văn bản siêu dài cần chia nhỏ thành phụ đề"),
    delay_seconds: float = Form(4.0, description="Thời gian chờ giữa mỗi câu (giây)")
):
    """
    Tiếp nhận văn bản dài, tự động chia thành các câu ngắn và chạy ngầm (chữ chạy) trên OBS.
    """
    if not source_name or not text_content:
        raise HTTPException(status_code=400, detail="Thiếu tham số source_name hoặc text_content.")
        
    # Ném tác vụ xuống Background để API trả về kết quả ngay lập tức (không bị treo)
    background_tasks.add_task(
        SubtitleStreamer.start_streaming,
        source_name=source_name,
        full_text=text_content,
        delay_seconds=delay_seconds
    )
    
    return {
        "status": "success",
        "message": f"Đã khởi động tiến trình chạy phụ đề ngầm cho nguồn '{source_name}'.",
        "delay_config": f"{delay_seconds} giây/câu"
    }

@router.post("/av_subtitle/start")
def start_av_subtitle_stream(
    background_tasks: BackgroundTasks,
    scene_name: str = Form(..., description="Tên cảnh (Scene) trong OBS"),
    text_source_name: str = Form(..., description="Tên nguồn Text trong OBS (VD: Text - MC)"),
    media_source_name: str = Form(..., description="Tên nguồn Media trong OBS (VD: Audio - MC)"),
    text_content: str = Form(..., description="Đoạn văn bản siêu dài"),
    ref_audio_file: UploadFile = File(None, description="Tùy chọn: Upload file âm thanh mẫu (giọng clone)")
):
    """
    Chạy phụ đề đồng bộ với giọng nói từ OmniVoice.
    """
    if not text_source_name or not text_content:
        raise HTTPException(status_code=400, detail="Thiếu tham số bắt buộc.")
        
    # Lưu file âm thanh mẫu nếu người dùng có upload
    ref_audio_path = None
    if ref_audio_file and ref_audio_file.filename:
        os.makedirs("uploads/custom_ref", exist_ok=True)
        ref_audio_path = os.path.abspath(f"uploads/custom_ref/{ref_audio_file.filename}")
        with open(ref_audio_path, "wb") as buffer:
            shutil.copyfileobj(ref_audio_file.file, buffer)
        
    # Import ở đây để tránh lỗi vòng lặp (circular import)
    from workflow.av_streamer import AVStreamer
        
    background_tasks.add_task(
        AVStreamer.start_streaming,
        scene_name=scene_name,
        text_source_name=text_source_name,
        media_source_name=media_source_name,
        full_text=text_content,
        ref_audio_path=ref_audio_path
    )
    
    return {
        "status": "success",
        "message": "Đã khởi động tiến trình AV Streaming ngầm (Phụ đề + Giọng nói)."
    }
