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
import json
import os

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

load_dotenv()

ZAPIER_MCP_URL = os.getenv("ZAPIER_MCP_URL", "").strip()
ZAPIER_MCP_API_KEY = os.getenv("ZAPIER_MCP_API_KEY", "").strip()


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def main():
    # Fail fast with clear setup errors so students know what to fix in .env.
    if not ZAPIER_MCP_URL:
        raise RuntimeError("Missing ZAPIER_MCP_URL in .env")
    if not ZAPIER_MCP_API_KEY:
        raise RuntimeError("Missing ZAPIER_MCP_API_KEY in .env")

    # Transport = "how" we connect to MCP. Here: streamable HTTP + bearer auth.
    transport = StreamableHttpTransport(
        ZAPIER_MCP_URL,
        headers={"Authorization": f"Bearer {ZAPIER_MCP_API_KEY}"},
    )

    # Client = high-level MCP interface (list tools, call tools, etc.).
    client = Client(transport=transport)

    print_header("13 - MCP List Tools")
    print("Connecting to Zapier MCP...")

    # Use async context manager so the network session opens/closes cleanly.
    async with client:
        # Ask MCP server for tool metadata.
        tools = await client.list_tools()

        print("\nAvailable tools:")
        for tool in tools:
            # Each tool has a machine name and a human-friendly description.
            print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
