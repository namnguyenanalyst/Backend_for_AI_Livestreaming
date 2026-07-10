import os
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from core.logger import get_logger
from core.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, SYSTEM_INSTRUCTIONS

logger = get_logger("LLMClient")

class LLMClient:
    def __init__(self):
        self.api_key = LLM_API_KEY
        self.base_url = LLM_BASE_URL
        self.model = LLM_MODEL
        
        # Nếu chưa có API key, ta log cảnh báo nhưng không crash ngay
        if not self.api_key:
            logger.warning("LLM_API_KEY chưa được cấu hình trong .env!")

        self.client = AsyncOpenAI(
            api_key=self.api_key or "DUMMY_KEY",
            base_url=self.base_url
        )

    def get_system_instruction(self, instruction_key: str = "default") -> str:
        return SYSTEM_INSTRUCTIONS.get(instruction_key, SYSTEM_INSTRUCTIONS.get("default", ""))

    async def generate_stream(self, prompt: str, instruction_key: str = "default") -> AsyncGenerator[str, None]:
        """
        Gọi API LLM và trả về stream các token.
        """
        if not self.api_key:
            yield "Lỗi: Chưa cấu hình LLM_API_KEY trong hệ thống."
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
            logger.error(f"Lỗi khi gọi LLM API: {str(e)}")
            yield f"\n[Lỗi kết nối LLM: {str(e)}]"

    async def generate_text(self, prompt: str, instruction_key: str = "default") -> str:
        """
        Gọi API LLM ở chế độ Non-streaming (Đợi sinh xong toàn bộ).
        Đã loại bỏ chức năng Tool Calling phức tạp để tối ưu tốc độ và chi phí.
        """
        if not self.api_key:
            return "Lỗi: Chưa cấu hình LLM_API_KEY trong hệ thống."

        system_prompt = self.get_system_instruction(instruction_key)
        
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt += f"\n\n[CRITICAL SYSTEM NOTE: Today's real date is {current_date}. You MUST use this exact date (Year and Month) when generating content.]"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        logger.info(f"Đang gửi request NON-STREAM tới {self.model} (instruction: {instruction_key})")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            
            message = response.choices[0].message
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
            logger.error(f"Lỗi khi gọi LLM API (Non-stream): {str(e)}")
            return f"\n[Lỗi kết nối LLM: {str(e)}]"

# Khởi tạo một singleton client
llm_client = LLMClient()
