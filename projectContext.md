# PROJECT CONTEXT

## Mục tiêu dự án

Tôi đang xây dựng một nền tảng AI Livestream tự động.

Mục tiêu cuối cùng là tạo một hệ thống backend có thể điều phối toàn bộ quá trình livestream, bao gồm:

- Điều khiển OBS Studio thông qua obs-websocket (Không cần UI của OBS)
- Tích hợp Whisper (Speech-to-Text) - Thông qua API độc lập
- Tích hợp OmniVoice (Text-to-Speech) - Thông qua API độc lập
- Tích hợp LLM - Thông qua API độc lập (Coming soon)
- Xử lý ảnh (Coming soon)
- Xử lý âm thanh (Coming soon)
- Quản lý workflow livestream (Coming soon)
- Sau này có thể mở rộng thêm nhiều AI module khác (Coming soon).

Backend sẽ là trung tâm điều phối (Orchestrator), còn OBS chỉ là một thành phần được backend điều khiển.

---

## Công nghệ sử dụng

- **Ngôn ngữ & Framework:** Python 3, FastAPI.
- **Môi trường ảo:** `venv`.
- **Message Broker (Event Bus):** Redis (Pub/Sub).
- **Giao tiếp OBS:** `obs-websocket-py` (v5).

---

## OBS hiện tại

Tôi đang sử dụng:
OBS Studio (Bản di động - Portable)
OBS đã tích hợp sẵn obs-websocket (cổng `4455`).

Backend sẽ kết nối tới: `ws://localhost:4455` để điều khiển OBS.

---

## Điều tôi KHÔNG muốn

- Tôi không muốn sửa mã nguồn OBS.
- Tôi cũng không muốn nhúng code trực tiếp vào OBS.
- Các AI Model (Whisper, OmniVoice) KHÔNG tích hợp chung mã nguồn với Backend để tránh nặng hệ thống. Backend chỉ đóng vai trò là API Client gọi tới chúng.
- OBS chỉ đóng vai trò render livestream. Toàn bộ logic điều phối nằm ở backend.

---

## Vai trò của Backend

Backend (Orchestrator) sẽ điều khiển:
- OBS Controller (Các lệnh WebSocket)
- API Clients (Whisper, OmniVoice, LLM)
- Workflow
- Xử lý Event thông qua Redis Event Bus.

Các module giao tiếp với nhau theo cơ chế Event-Driven thay vì gọi trực tiếp.

---

## Kiến trúc mong muốn

AI Livestream Backend

├── Core (Config, Logger, Redis Event Bus)
├── OBS Controller (Adapter điều khiển OBS)
├── API Clients (Whisper, OmniVoice, LLM)
├── Workflow Engine
├── Event Bus
├── Input Manager
├── Output Manager
└── Plugin System

---

## OBS Controller

Backend có một module riêng: `obs/`
Chịu trách nhiệm hoàn toàn mọi thao tác trên OBS:
- Quản lý kết nối (`controller.py`)
- Quản lý Phân cảnh: Thêm, xóa, chuyển cảnh (`scene.py`)
- Quản lý Nguồn: Tạo, xóa nguồn (như Text, Image, Media, Capture), bật/tắt, thay đổi kích thước (`source.py`)
- Quản lý Văn bản/Phụ đề (`text.py`)
- Quản lý Âm thanh (`audio.py`)
- Quản lý Media (`media.py`)
- Quản lý luồng và ghi hình (`stream.py`)
- Lắng nghe Event từ OBS (`events.py`)

Các module khác KHÔNG được gọi WebSocket trực tiếp, mà phải gọi qua các hàm của `obs/`.

---

## Event Driven Architecture (Redis)

Hệ thống xây dựng theo Event Driven thông qua Redis.
Ví dụ:
`Microphone Input` -> (gọi API) -> `Whisper Client` -> `Publish Event "SpeechRecognized"` -> `Redis Event Bus` -> `Workflow Engine` -> `Publish Event "UpdateSubtitle"` -> `OBS Controller (Text)`.

Mọi thứ thông qua `core/event_bus.py`.

---

## Workflow Engine

Workflow sẽ subscribe các kênh trên Redis và điều phối toàn bộ luồng logic từ khi User nói đến khi OBS phát Audio và hiển thị Subtitle.

---

## Dự kiến cấu trúc Project

```
backend/
├── app.py (FastAPI entrypoint)
├── core/
│   ├── config.py
│   ├── logger.py
│   └── event_bus.py (Redis Pub/Sub)
├── obs/
│   ├── controller.py (Kết nối WS)
│   ├── scene.py
│   ├── source.py
│   ├── audio.py
│   ├── media.py
│   ├── text.py
│   ├── stream.py
│   └── events.py
├── clients/ (Gọi ra dịch vụ ngoài)
│   ├── whisper_client.py
│   ├── omnivoice_client.py
│   ├── llm_client.py
│   └── image_client.py
├── workflow/
│   ├── engine.py
│   ├── talking.py
│   └── livestream.py
├── plugins/
└── tests/
```

---

## Giai đoạn phát triển

**Phase 1: Xây dựng OBS Controller (ĐÃ HOÀN THÀNH)**
Hoàn thiện Core, Redis Event Bus và module điều khiển OBS hoàn chỉnh (Scene, Source, Text, Audio, Media).

**Phase 2: Xây dựng Backend API**
Tạo các FastAPI endpoint để phơi bày chức năng của OBS ra bên ngoài nếu cần.

**Phase 3: Tích hợp AI Clients**
Xây dựng các module gọi HTTP/WS tới Whisper, OmniVoice, LLM.

**Phase 4: Input Pipeline**
Thu thập luồng âm thanh, hình ảnh để truyền vào cho AI xử lý.

**Phase 5: Workflow Engine**
Điều phối toàn bộ quá trình livestream, gắn kết AI và OBS thông qua Redis Event Bus.

**Phase 6: Plugin System**
Cho phép mở rộng (Thời tiết, Chat, Avatar...) không cần sửa core.

---

## Nguyên tắc thiết kế

- Backend là trung tâm Orchestrator.
- OBS là Adapter nhận lệnh qua WebSocket.
- Tách bạch AI Models ra khỏi Backend, gọi qua API.
- Kiến trúc hướng Service và Event-Driven qua Redis.
- Dễ mở rộng và bảo trì.