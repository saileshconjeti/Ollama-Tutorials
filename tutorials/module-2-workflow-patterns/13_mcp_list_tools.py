"""
13_mcp_list_tools.py

Teaching goal:
- Show the smallest possible MCP client flow:
  1) connect to an MCP server
  2) list available tools
  3) print what each tool does

Why this matters:
- In agent workflows, tool discovery is usually step zero.
- Before calling tools, we need to know their exact names/capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import print_actionable_error, print_ascii_tree, print_header, print_kv, print_step

load_dotenv(override=True)

ZAPIER_MCP_URL = os.getenv("ZAPIER_MCP_URL", "").strip()
ZAPIER_MCP_API_KEY = os.getenv("ZAPIER_MCP_API_KEY", "").strip()

LEGACY_ZAPIER_MCP_URL = "https://mcp.zapier.com/api/v1/connect"


def validate_zapier_mcp_config() -> None:
    """Fail fast when the Zapier MCP setup is missing or uses a stale endpoint."""
    if not ZAPIER_MCP_URL:
        print_actionable_error(
            "ZAPIER_MCP_URL is missing in .env.",
            "The MCP client needs the server URL before it can discover available tools.",
            [
                "Open Zapier MCP and copy your Streamable HTTP server URL.",
                "Add ZAPIER_MCP_URL=your_server_url to .env.",
                "Re-run this script.",
            ],
        )
        raise SystemExit(1)
    has_url_token = "token=" in ZAPIER_MCP_URL
    if not ZAPIER_MCP_API_KEY and not has_url_token:
        print_actionable_error(
            "ZAPIER_MCP_API_KEY is missing.",
            "The MCP server requires authentication before it will list tools.",
            [
                "Add ZAPIER_MCP_API_KEY=your_key_here to .env.",
                "Or use a ZAPIER_MCP_URL that already includes a token parameter.",
                "Re-run this script.",
            ],
        )
        raise SystemExit(1)
    if not has_url_token and ZAPIER_MCP_URL.rstrip("/") == LEGACY_ZAPIER_MCP_URL:
        raise RuntimeError(
            "ZAPIER_MCP_URL is set to Zapier's old generic connect endpoint.\n"
            "Open Zapier MCP, copy the Streamable HTTP server URL for your MCP server, "
            "and use that full URL in .env.\n"
            "The value usually looks like a Zapier MCP server-specific URL, not "
            f"{LEGACY_ZAPIER_MCP_URL}."
        )


async def main():
    # Fail fast with clear setup errors so students know what to fix in .env.
    validate_zapier_mcp_config()

    # Transport = "how" we connect to MCP. Here: streamable HTTP + bearer auth.
    headers = {"Authorization": f"Bearer {ZAPIER_MCP_API_KEY}"} if ZAPIER_MCP_API_KEY else {}
    transport = StreamableHttpTransport(
        ZAPIER_MCP_URL,
        headers=headers,
    )

    # Client = high-level MCP interface (list tools, call tools, etc.).
    client = Client(transport=transport)

    print_header("MCP Tool Discovery")
    print("What this demonstrates: before an agent can call tools, it should discover the exact tool names and descriptions.")

    print_step(1, "Inspecting MCP data flow")
    print_ascii_tree(
        """
        Python MCP Client
            |
            v
        Zapier MCP Server
            |
            v
        Tool Metadata
            |
            v
        Terminal Tool List
        """
    )

    print_step(2, "Checking MCP configuration")
    print_kv("MCP URL configured", bool(ZAPIER_MCP_URL))
    print_kv("API key configured", bool(ZAPIER_MCP_API_KEY))

    print_step(3, "Connecting to Zapier MCP")

    # Use async context manager so the network session opens/closes cleanly.
    async with client:
        # Ask MCP server for tool metadata.
        tools = await client.list_tools()

        print_step(4, "Available tools returned by MCP")
        print_kv("Tool count", len(tools))
        for tool in tools:
            # Each tool has a machine name and a human-friendly description.
            print(f"- {tool.name}: {tool.description}")

    print_step(5, "What to observe")
    print("Tool names are machine-readable contracts. Later scripts choose one of these names and pass structured arguments.")


if __name__ == "__main__":
    asyncio.run(main())
