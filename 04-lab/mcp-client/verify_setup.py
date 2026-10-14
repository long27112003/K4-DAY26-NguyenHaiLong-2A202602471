#!/usr/bin/env python3
"""
Verification script for Weather Agent setup
Checks if all components are configured correctly
"""
import asyncio
import os
import sys
from pathlib import Path

CLIENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CLIENT_DIR.parents[1]

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def check_environment():
    """Check if .env file exists and is configured"""
    print("🔍 Checking environment configuration...")

    env_files = [CLIENT_DIR / ".env", REPO_ROOT / ".env"]
    existing_env_files = [path for path in env_files if path.exists()]
    if not existing_env_files:
        print("❌ Không tìm thấy .env trong mcp-client hoặc thư mục gốc repo")
        print("   Sao chép .env.example thành .env rồi điền API key")
        return False

    from dotenv import load_dotenv

    for env_file in existing_env_files:
        load_dotenv(env_file)

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    placeholders = {"...", "your_key", "your_gemini_api_key", "your_google_api_key_here"}
    if not api_key or api_key.strip() in placeholders:
        print("❌ GOOGLE_API_KEY/GEMINI_API_KEY chưa được cấu hình")
        print("   Get key from: https://aistudio.google.com/apikey")
        return False

    # Google ADK đọc GOOGLE_API_KEY; dùng lại key của bài 01 khi cần.
    os.environ.setdefault("GOOGLE_API_KEY", api_key)
    print("✅ Gemini API key configured (value hidden)")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        ("google.adk", "Google ADK"),
        ("google.genai", "Google GenAI SDK"),
        ("mcp", "MCP"),
        ("fastmcp", "FastMCP"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n   Install with: uv sync")
        print("   Or: pip install google-adk google-genai mcp fastmcp python-dotenv httpx")
    
    return all_installed

def check_agent_structure():
    """Check if agent directory structure is correct"""
    print("\n🔍 Checking agent structure...")
    
    required_files = [
        "weather_agent/agent.py",
        "weather_agent/__init__.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = CLIENT_DIR / file_path
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist

def check_mcp_server():
    """Perform a real MCP handshake and call the health_check tool."""
    print("\n🔍 Checking MCP server connectivity...")

    # Cùng URL mà weather_agent/agent.py dùng (biến môi trường MCP_SERVER_URL)
    from dotenv import load_dotenv

    load_dotenv(CLIENT_DIR / ".env")
    load_dotenv(REPO_ROOT / ".env")
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")

    async def probe_server() -> tuple[list[str], str]:
        from fastmcp import Client

        async with Client(server_url, timeout=10.0) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            result = await client.call_tool("health_check", {})
            health_text = result.content[0].text
            return tool_names, health_text

    try:
        tool_names, health_text = asyncio.run(probe_server())
        expected = {"get_current_weather", "get_forecast", "health_check"}
        missing = expected.difference(tool_names)
        if missing:
            print(f"❌ MCP server thiếu tool: {sorted(missing)}")
            return False

        print(f"✅ MCP handshake successful at {server_url}")
        print(f"   Tools: {', '.join(tool_names)}")
        print(f"   health_check: {health_text}")
        if not health_text.startswith("✅"):
            print("❌ MCP server chưa sẵn sàng gọi WeatherAPI; hãy cấu hình WEATHERAPI_KEY")
            return False
        return True
    except Exception as e:  # noqa: BLE001 - diagnostic must report any connection failure
        print(f"❌ Cannot reach MCP server at {server_url}: {e}")
        print("   Start it: cd ../mcp-server && uv run python weather.py")
        return False

def check_agent_import():
    """Try to import the agent"""
    print("\n🔍 Checking agent import...")
    
    try:
        # Suppress warnings during import
        import warnings
        warnings.filterwarnings("ignore")
        
        from weather_agent import root_agent
        print(f"✅ Agent imported successfully: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        return True
    except Exception as e:  # noqa: BLE001 - diagnostic must report any import failure
        print(f"❌ Failed to import agent: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Weather Agent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_agent_structure(),
        check_mcp_server(),
        check_agent_import(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed!")
        print("\n🚀 Ready to start!")
        print("   Run: uv run adk web")
        print("\n📍 Then open: http://localhost:8000")
        return 0
    else:
        print("❌ Some checks failed")
        print("\n⚠️  Fix the issues above and run this script again")
        return 1

if __name__ == "__main__":
    sys.exit(main())

