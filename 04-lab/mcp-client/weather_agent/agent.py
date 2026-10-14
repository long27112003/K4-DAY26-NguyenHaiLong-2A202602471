"""
Weather Agent - Connects to Remote MCP Server on Cloud Run
Successfully connects to custom MCP HTTP endpoints!
"""
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Ưu tiên cấu hình riêng của MCP client, sau đó mới dùng .env ở gốc repo.
CLIENT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(CLIENT_DIR / ".env")
load_dotenv(CLIENT_DIR.parents[1] / ".env")

# Google ADK dùng GOOGLE_API_KEY; cho phép tái sử dụng GEMINI_API_KEY của bài 01.
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
if os.getenv("GOOGLE_API_KEY"):
    os.environ.pop("GEMINI_API_KEY", None)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mặc định: server chạy local. Deploy lên Cloud Run thì đặt MCP_SERVER_URL trong .env
# (ví dụ: https://<service>.run.app/mcp). verify_setup.py đọc cùng biến này.
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")

logger.info("Initializing weather agent with remote MCP server")
logger.info("MCP Server: %s", MCP_SERVER_URL)

try:
    # Create connection parameters for the remote MCP server
    connection_params = StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        timeout=30.0,  # Increased timeout for Cloud Run cold starts
    )
    
    # Create the MCP toolset - this will connect to the remote server
    logger.info("Configuring MCP connection...")
    weather_tools = McpToolset(
        connection_params=connection_params,
    )
    logger.info("MCP toolset created successfully")
    
    # Create the agent with remote MCP tools
    root_agent = Agent(
        name="weather_agent",
        model="gemini-3.8-flash",
        description="Weather assistant backed by live MCP weather tools.",
        instruction=(
            "Always use the available MCP weather tools for weather questions. "
            "Do not invent weather values. Clearly state any tool error and ask the "
            "user to retry when live data is unavailable."
        ),
        tools=[weather_tools],
    )
    logger.info("Weather agent initialized with remote MCP tools:")
    logger.info("   - get_current_weather(city)")
    logger.info("   - get_forecast(city, days)")
    logger.info("   - health_check()")
    logger.info("MCP toolset configured; connection is verified on first use")
    
except Exception as e:  # noqa: BLE001 - fall back when any toolset setup step fails
    logger.error("Failed to configure remote MCP server: %s", e)
    logger.error("   Server URL: %s", MCP_SERVER_URL)
    import traceback
    traceback.print_exc()
    
    # Create a fallback agent without tools
    logger.warning("Creating fallback agent without MCP tools")
    root_agent = Agent(
        name="weather_agent",
        model="gemini-3.8-flash",
    )

