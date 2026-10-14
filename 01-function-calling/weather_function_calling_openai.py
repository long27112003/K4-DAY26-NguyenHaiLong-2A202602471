"""Minh hoạ FUNCTION CALLING thuần với OpenAI Python SDK.

Tool `get_weather` được định nghĩa schema thủ công VÀ thực thi ngay trong
chính file app này. Model chỉ QUYẾT ĐỊNH gọi tool nào; app mới là nơi chạy.

Cách chạy:
    pip install -r ../requirements.txt
    # Thiết lập API key:
    # PowerShell: $env:OPENAI_API_KEY="sk-..."
    # hoặc điền OPENAI_API_KEY=sk-... vào file .env
    python weather_function_calling_openai.py
"""

import json
import os
import sys
from pathlib import Path

from openai import OpenAI

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY or API_KEY.strip() in ("...", "your_openai_api_key", "your_key"):
    raise RuntimeError(
        "Thiếu OPENAI_API_KEY. "
        "Hãy đặt key trong biến môi trường hoặc file .env ở thư mục gốc repo."
    )

client = OpenAI(api_key=API_KEY)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_INSTRUCTION = (
    "Bạn là trợ lý thời tiết thân thiện, trả lời bằng tiếng Việt tự nhiên. "
    "Dùng emoji phù hợp (🌧️ 🌤️ 💨 💧). "
    "Tóm tắt ngắn gọn, dễ hiểu, và đưa ra lời khuyên thực tế "
    "(ví dụ: mang ô, mặc áo mỏng, ...)."
)

# 1. App tự định nghĩa schema của tool theo chuẩn OpenAI Tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Lấy thời tiết hiện tại của một thành phố",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Tên thành phố (ví dụ: Hà Nội, Đà Nẵng, Hồ Chí Minh)",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


# 2. App tự thực thi tool (mock data hoặc gọi API thật)
def get_weather(city: str) -> str:
    """Trả về thời tiết (mock) của *city*. Dùng làm tool cho model."""
    mock_data = {
        "Hà Nội": {
            "nhiệt_độ": "29°C",
            "thời_tiết": "trời mưa nhẹ",
            "độ_ẩm": "82%",
            "gió": {"hướng": "Đông Nam", "tốc_độ": "12 km/h"},
        },
        "Hồ Chí Minh": {
            "nhiệt_độ": "33°C",
            "thời_tiết": "mưa rào",
            "độ_ẩm": "75%",
            "gió": {"hướng": "Tây Nam", "tốc_độ": "15 km/h"},
        },
        "Đà Nẵng": {
            "nhiệt_độ": "30°C",
            "thời_tiết": "nhiều mây",
            "độ_ẩm": "78%",
            "gió": {"hướng": "Đông", "tốc_độ": "10 km/h"},
        },
    }

    default = {"nhiệt_độ": "28°C", "thời_tiết": "không có dữ liệu chi tiết"}
    return json.dumps({"city": city, **mock_data.get(city, default)}, ensure_ascii=False)


def run(prompt: str) -> str:
    """Gửi *prompt* tới OpenAI, tự động xử lý function calling và trả về câu trả lời cuối."""
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": prompt},
    ]

    # 3. Gọi model — model quyết định có gọi tool hay không
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    response_message = response.choices[0].message

    # 4. Vòng lặp: nếu model yêu cầu gọi tool, app TỰ THỰC THI rồi gửi lại kết quả
    while response_message.tool_calls:
        # Lưu câu trả lời kèm tool_calls của model vào messages
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"  [model yêu cầu] {func_name}({args})")
            if func_name == "get_weather":
                result = get_weather(**args)
            else:
                result = json.dumps({"error": f"Không tìm thấy tool {func_name}"})

            print(f"  [app thực thi]  -> {result}")

            # Đưa kết quả thực thi tool vào lịch sử hội thoại với tool_call_id
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

        # Gửi lại toàn bộ hội thoại để model tiếp tục xử lý
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        response_message = response.choices[0].message

    # 5. Model tổng hợp câu trả lời cuối cùng
    return response_message.content or ""


if __name__ == "__main__":
    question = "Thời tiết Hà Nội và Đà Nẵng hôm nay thế nào?"
    print(f"User: {question}\n")
    print("Trả lời:", run(question))
