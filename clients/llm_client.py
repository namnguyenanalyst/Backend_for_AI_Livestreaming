import os
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from core.logger import get_logger
from core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SYSTEM_INSTRUCTIONS

logger = get_logger("DeepseekClient")

class DeepseekClient:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.model = DEEPSEEK_MODEL
        
        # Nếu chưa có API key, ta log cảnh báo nhưng không crash ngay
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY chưa được cấu hình trong .env!")

        self.client = AsyncOpenAI(
            api_key=self.api_key or "DUMMY_KEY",
            base_url=self.base_url
        )

    def get_system_instruction(self, instruction_key: str = "default") -> str:
        return SYSTEM_INSTRUCTIONS.get(instruction_key, SYSTEM_INSTRUCTIONS.get("default", ""))

    async def generate_stream(self, prompt: str, instruction_key: str = "default") -> AsyncGenerator[str, None]:
        """
        Gọi API Deepseek và trả về stream các token.
        """
        if not self.api_key:
            yield "Lỗi: Chưa cấu hình DEEPSEEK_API_KEY trong hệ thống."
            return

        system_prompt = self.get_system_instruction(instruction_key)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        logger.info(f"Đang gửi request tới {self.model} (instruction: {instruction_key})")
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"Lỗi khi gọi Deepseek API: {str(e)}")
            yield f"\n[Lỗi kết nối Deepseek: {str(e)}]"

    async def generate_text(self, prompt: str, instruction_key: str = "default") -> str:
        """
        Gọi API Deepseek ở chế độ Non-streaming (Đợi sinh xong toàn bộ).
        """
        if not self.api_key:
            return "Lỗi: Chưa cấu hình DEEPSEEK_API_KEY trong hệ thống."

        system_prompt = self.get_system_instruction(instruction_key)
        
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt += f"\n\n[CRITICAL SYSTEM NOTE: Today's real date is {current_date}. You MUST use this exact date (Year and Month) when searching for the latest news. DO NOT search for 2024 or 2025.]"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        logger.info(f"Đang gửi request NON-STREAM tới {self.model} (instruction: {instruction_key})")
        
        from clients.search_client import search_internet
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Tìm kiếm thông tin cập nhật trên internet. Dùng khi cần dữ liệu thực tế, tin tức mới nhất.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Câu truy vấn tìm kiếm"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        try:
            MAX_ITERATIONS = 5
            iteration = 0
            
            while iteration <= MAX_ITERATIONS:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                }
                
                # Nếu chưa quá giới hạn, cấp tool cho nó. Nếu quá rồi, cắt hoàn toàn tool.
                if iteration < MAX_ITERATIONS:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"
                
                response = await self.client.chat.completions.create(**kwargs)
                
                message = response.choices[0].message
                
                # Nếu AI yêu cầu dùng Tool
                if message.tool_calls:
                    logger.info(f"Vòng {iteration+1}: AI yêu cầu gọi {len(message.tool_calls)} Tool(s)")
                    
                    assistant_msg = message.model_dump(exclude_none=True)
                    messages.append(assistant_msg)
                    
                    for tool_call in message.tool_calls:
                        if tool_call.function.name == "search_internet":
                            try:
                                args = json.loads(tool_call.function.arguments)
                                query = args.get("query", "")
                                search_result = search_internet(query) # đã mặc định max_results=10 bên trong
                                
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call.function.name,
                                    "content": search_result
                                })
                            except Exception as tool_e:
                                logger.error(f"Lỗi khi thực thi tool: {tool_e}")
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call.function.name,
                                    "content": f"Lỗi hệ thống: {tool_e}"
                                })
                    
                    iteration += 1
                else:
                    # Hoàn thành, AI không yêu cầu gọi tool nữa, trả về kết quả
                    content = message.content or ""
                    reasoning = getattr(message, "reasoning_content", None)
                    
                    # Trả về content sạch sẽ. Chỉ dùng reasoning nếu content hoàn toàn rỗng.
                    if not content.strip() and reasoning:
                        final_text = reasoning
                    else:
                        final_text = content
                        
                    # Dùng bộ lọc để dọn dẹp các ký tự junk, emoji, markdown thừa
                    from core.text_utils import clean_junk_text
                    return clean_junk_text(final_text)
                        
        except Exception as e:
            logger.error(f"Lỗi khi gọi Deepseek API (Non-stream): {str(e)}")
            return f"\n[Lỗi kết nối Deepseek: {str(e)}]"

# Khởi tạo một singleton client
deepseek_client = DeepseekClient()
