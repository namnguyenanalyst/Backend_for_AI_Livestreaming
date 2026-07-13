# AI Livestreaming Backend

Đây là hệ thống Backend tự động hóa hoàn toàn quy trình Livestream bằng Trí tuệ Nhân tạo (AI). Hệ thống có khả năng tự động cập nhật tin tức thị trường, sử dụng LLM để biên soạn kịch bản, chuyển đổi văn bản thành giọng nói (TTS) qua OmniVoice, và điều khiển trực tiếp phần mềm OBS Studio để phát sóng.

## Tính Năng Chính
- **Tự động hóa Kịch bản (Auto-Generator):** Tự động gọi API của LLM (ví dụ: Gemini) để tạo ra kịch bản Livestream dài hạn dựa trên tin tức thị trường mới nhất.
- **Hệ Thống Hàng Đợi (Queue):** Tích hợp Redis để quản lý luồng văn bản và âm thanh, đảm bảo việc phát sóng diễn ra mượt mà, liên tục mà không bị gián đoạn hay trùng lặp.
- **API Linh Hoạt:** Cung cấp các endpoint RESTful API (FastAPI) giúp dễ dàng tích hợp với Postman hoặc các hệ thống Frontend khác.

## Yêu Cầu Hệ Thống
- Python 3.10+
- Redis Server (đang chạy ở background)
- OBS Studio (đã cài đặt plugin OBS WebSocket)
- Môi trường ảo (Virtual Environment) được khuyến nghị.

## Cài Đặt

1. **Clone dự án và truy cập vào thư mục gốc:**
   ```bash
   cd Backend_for_AI_Livestreaming
   ```

2. **Kích hoạt môi trường ảo (Virtual Environment):**
   ```bash
   source venv/bin/activate
   ```
   *(Nếu chưa có, hãy tạo mới bằng lệnh: `python -m venv venv`)*

3. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Lưu ý: Dự án sử dụng thư viện `inflect` để dịch số thành chữ cho luồng âm thanh).*

## Cấu Hình Môi Trường (.env)

Tạo một file `.env` ở thư mục gốc của dự án và điền các thông số cấu hình của bạn. **KHÔNG** chia sẻ file này cho bất kỳ ai.

```env
# Cấu hình OBS WebSocket
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_obs_password_here

# Cấu hình Redis
REDIS_URL=redis://localhost:6379

# Cấu hình LLM AI (Ví dụ: Gemini)
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=https://api.your-llm-provider.com/v1
LLM_MODEL=gemini-3.5-flash

# Cấu hình OmniVoice (TTS)
OMNIVOICE_API_URL=http://<your_omnivoice_ip>:8002/clone_voice
WEBHOOK_URL=http://localhost:8000/api/webhook/omnivoice
WEBHOOK_SECRET=your_webhook_secret_here
DEFAULT_REF_AUDIO=uploads/ref_audio.wav
```

## Chạy Ứng Dụng

Sau khi đã hoàn tất cấu hình, bạn có thể khởi động server FastAPI bằng lệnh sau:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

- Hệ thống sẽ chạy tại địa chỉ: `http://localhost:8000`
- Bạn có thể truy cập tài liệu API tự động (Swagger UI) tại: `http://localhost:8000/docs`

## Luồng Hoạt Động Của Hệ Thống (Workflow)

Hệ thống hoạt động dựa trên 3 luồng xử lý ngầm (Background Tasks) chính chạy song song:
1. **AutoGenerator Task:** Theo dõi hàng đợi văn bản trong Redis. Khi sắp hết nội dung (< 5 câu), tự động gọi LLM sinh kịch bản mới, cắt thành từng câu nhỏ và nạp vào hàng đợi.
2. **Prefetcher Task:** Lấy các câu text từ hàng đợi, đưa qua bộ lọc Normalizer (biến số thành chữ tiếng Anh) và gửi đến OmniVoice để tạo file Audio.
3. **Streamer Task:** Lấy file Audio và đoạn Text gốc tương ứng, đồng bộ đưa lên OBS để hiển thị phụ đề và phát âm thanh.

## Cách Tương Tác Qua Postman
Dự án có đính kèm file `AI Livestream Backend (Full API).postman_collection.json`. Bạn có thể Import file này vào Postman để:
- Thay đổi System Prompt hoặc User Prompt cho AI.
- Cập nhật linh hoạt câu lệnh điều hướng cho bản tin (Ví dụ: Yêu cầu AI cập nhật giá Bitcoin mới nhất).
- Kích hoạt việc tạo kịch bản từ xa.

## Lưu ý Bảo Mật
- Không đưa các key API (như `LLM_API_KEY`) hoặc mật khẩu OBS lên public repository. Luôn giữ chúng an toàn trong file `.env`.
- Chỉ cho phép các IP đáng tin cậy truy cập vào port `8000` và cấu hình bảo mật đúng mức cho Webhook.
