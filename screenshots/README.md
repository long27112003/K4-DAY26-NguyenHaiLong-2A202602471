# Checklist ảnh nộp bài

Chạy lệnh bằng **Windows PowerShell**. Tất cả ảnh PNG được lưu trực tiếp trong
thư mục này. Không để API key, file `.env`, token hoặc lịch sử lệnh chứa key xuất
hiện trong ảnh.

## Danh sách tên ảnh

| STT | Tên file | Bằng chứng cần thấy |
|---:|---|---|
| 1 | `01-function-calling.png` | Model yêu cầu tool, app thực thi, câu trả lời cuối |
| 2 | `02-mcp-basics.png` | `list_tools` và các kết quả `call_tool` |
| 3 | `02-claude-mcp-connected.png` | Claude báo MCP `weather` là `Connected` |
| 4 | `02-claude-tool-call.png` *(tùy chọn)* | Claude thật sự gọi `get_weather` và trả kết quả; cần Claude Pro/Max hoặc Anthropic API có billing |
| 5 | `03-auth.png` | Auth server và auth client chạy thành công |
| 6 | `03-registry.png` | Registry tìm tool và chọn `get_weather_v2` |
| 7 | `03-versioning.png` | Metadata, deprecated v1 và kết quả v2 |
| 8 | `04-lab-verify.png` | `All checks passed!` và đủ ba MCP tools |
| 9 | `04-lab-mcp-server.png` | Server HTTP chạy và nhận `CallToolRequest` |
| 10 | `04-lab-adk-web.png` | ADK Web: câu hỏi, tool call và kết quả thời tiết thật |

`01-function-calling.png` là tên được đề bài xác nhận trực tiếp. Các ảnh còn lại
dùng cùng quy ước `<phần>-<nội-dung>.png` để giảng viên dễ đối chiếu.

Có 9 ảnh bằng chứng chính. `02-claude-tool-call.png` là ảnh bổ sung; nếu tài khoản
Claude miễn phí không vào được Claude Code thì dùng `02-claude-mcp-connected.png`
để chứng minh MCP đã được đăng ký thành công, không cần mua gói chỉ để chụp ảnh.

## 1. Function Calling

Mở PowerShell tại thư mục gốc repo:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location .\01-function-calling
Clear-Host
python .\weather_function_calling.py
```

Chụp toàn bộ đoạn có:

- Hai dòng `[model yêu cầu] get_weather(...)` cho Hà Nội và Đà Nẵng.
- Hai dòng `[app thực thi] -> ...`.
- Dòng `Trả lời:` và câu trả lời tiếng Việt.

Lưu thành `screenshots/01-function-calling.png`.

## 2. MCP Basics

```powershell
Set-Location ..\02-mcp-basics
Clear-Host
python .\weather_client.py
```

Chụp phần `Tools server cung cấp` và kết quả Hanoi, Danang, Haiphong. Lưu thành
`screenshots/02-mcp-basics.png`.

## 3. MCP đã đăng ký với Claude Code

Quay về thư mục gốc repo:

```powershell
Set-Location ..
Clear-Host
claude mcp list
```

Chụp dòng dạng:

```text
weather: ... - √ Connected
```

Lưu thành `screenshots/02-claude-mcp-connected.png`.

Nếu tài khoản có Claude Pro/Max hoặc Anthropic API đã bật billing, chạy tiếp:

```powershell
claude
```

Trong Claude Code nhập lần lượt:

```text
/mcp
Dùng tool get_weather để kiểm tra thời tiết Hanoi. Hãy nói rõ tên tool và kết quả nhận được.
```

Chụp màn hình có tool `get_weather`, arguments `city: Hanoi` và câu trả lời của
Claude. Lưu thành `screenshots/02-claude-tool-call.png`.

## 4. Production Auth

Mở **hai PowerShell**.

Terminal 1:

```powershell
Set-Location "E:\AI in Action VinUni\K4-DAY26-NguyenHaiLong-2A202602471"
.\.venv\Scripts\Activate.ps1
Set-Location .\03-production
Clear-Host
python .\auth_server.py
```

Terminal 2:

```powershell
Set-Location "E:\AI in Action VinUni\K4-DAY26-NguyenHaiLong-2A202602471"
.\.venv\Scripts\Activate.ps1
Set-Location .\03-production
Clear-Host
python .\auth_client.py
```

Đặt hai terminal cạnh nhau và chụp server đang chạy cùng client có `Tools (có
auth)` và `Kết quả: Hanoi...`. Lưu thành `screenshots/03-auth.png`.

Sau khi chụp, nhấn `Ctrl+C` ở terminal server để giải phóng port 8000.

## 5. Tool Registry

Trong terminal client đang ở `03-production`:

```powershell
Clear-Host
python .\registry_client.py
```

Ảnh phải thấy `Tìm thấy 2 tool(s)`, `Best match: get_weather_v2 v2.0.0` và
`Kết quả:`. Lưu thành `screenshots/03-registry.png`.

## 6. Versioning

```powershell
Clear-Host
python .\versioned_client.py
```

Ảnh phải thấy:

- `Server: weather-v2 v2.0.0`.
- `Deprecated tools: ['get_weather']`.
- Kết quả v1.
- JSON v2 có `forecast`.

Thu nhỏ terminal nếu cần để lấy đủ output. Lưu thành
`screenshots/03-versioning.png`.

## 7. Lab 04 — MCP server và verification

Mở **hai PowerShell mới**.

Terminal 1 — server:

```powershell
Set-Location "E:\AI in Action VinUni\K4-DAY26-NguyenHaiLong-2A202602471\04-lab\mcp-server"
uv sync --frozen
Clear-Host
uv run python .\weather.py
```

Giữ terminal này chạy.

Terminal 2 — client verification:

```powershell
Set-Location "E:\AI in Action VinUni\K4-DAY26-NguyenHaiLong-2A202602471\04-lab\mcp-client"
uv sync --frozen
Clear-Host
uv run python .\verify_setup.py
```

Chụp terminal 2 có:

- `MCP handshake successful`.
- `get_current_weather, get_forecast, health_check`.
- `All checks passed!`.

Lưu thành `screenshots/04-lab-verify.png`.

## 8. Lab 04 — ADK Web gọi MCP thật

Giữ MCP server ở terminal 1. Tại terminal 2 chạy:

```powershell
Clear-Host
uv run adk web
```

Mở `http://localhost:8000`, chọn `weather_agent`, rồi gửi:

```text
Use the weather tools to tell me the current weather and a 3-day forecast for Hanoi.
```

Trong ADK Web, mở/expand tool trace nếu có. Chụp ảnh thấy câu hỏi, tool
`get_current_weather` hoặc `get_forecast`, arguments và câu trả lời thời tiết.
Lưu thành `screenshots/04-lab-adk-web.png`.

Sau khi agent trả lời, terminal MCP server sẽ có `CallToolRequest` và các request
`POST /mcp ... 200 OK`. Chụp terminal đó thành
`screenshots/04-lab-mcp-server.png`.

Cuối cùng nhấn `Ctrl+C` ở cả ADK Web và MCP server.

## 9. Kiểm tra trước khi commit

Từ thư mục gốc repo:

```powershell
Get-ChildItem .\screenshots\*.png | Select-Object Name, Length
git status --short
```

Phải có đủ các PNG ở bảng trên, mỗi file có `Length` lớn hơn 0, và không có file
`.env` nào xuất hiện trong `git status`.
