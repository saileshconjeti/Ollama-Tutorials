"""
14_mcp_direct_tool_call.py

Builds on:
- 13_mcp_list_tools.py

New concept:
- create a new Notion page through MCP
- retrieve the page URL and print it

Why this is the next step:
Searching by title can fail if the integration cannot see a page.
Creating a fresh page under a known parent is more reliable for a live demo.

Pattern:
1. Ask for a new page title
2. Create the page in Notion through MCP
3. Retrieve the created page by ID
4. Print the web link

Run:
    python tutorials/module-2-workflow-patterns/14_mcp_direct_tool_call.py
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError

from workflow_utils import print_header, print_subheader

load_dotenv()

ZAPIER_MCP_URL = os.getenv("ZAPIER_MCP_URL", "").strip()
ZAPIER_MCP_API_KEY = os.getenv("ZAPIER_MCP_API_KEY", "").strip()
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "").strip()

DEFAULT_NEW_PAGE_TITLE = "MCP Demo Page"


def get_new_page_title() -> str:
    """Read the new Notion page title from the terminal."""
    print_subheader("Enter a new Notion page title")
    print("Press Enter to use the default example.")
    print(f"Default: {DEFAULT_NEW_PAGE_TITLE}\n")

    title = input("New page title: ").strip()
    if not title:
        return DEFAULT_NEW_PAGE_TITLE
    return title


def format_result_content(result) -> str:
    """Convert MCP result content into readable text."""
    chunks = []
    for item in result.content:
        if hasattr(item, "text"):
            chunks.append(item.text)
        else:
            chunks.append(str(item))
    return "\n".join(chunks) if chunks else "[no text output returned]"


def try_parse_result_json(result) -> Any:
    """
    Try to parse the first text payload as JSON.
    Many MCP servers return JSON encoded as text, so parsing gives us
    structured fields like page_id/url for later logic.
    If parsing fails, return None.
    """
    if not result.content:
        return None

    first = result.content[0]
    text = getattr(first, "text", None)
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        return None


def find_first_value(data: Any, keys: tuple[str, ...]) -> str | None:
    """
    Recursively search dict/list content for the first matching key
    whose value is a non-empty string.
    This keeps the demo resilient when payload nesting differs by connector version.
    """
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value

        for value in data.values():
            found = find_first_value(value, keys)
            if found:
                return found

    elif isinstance(data, list):
        for item in data:
            found = find_first_value(item, keys)
            if found:
                return found

    return None


def get_tool_schema_map(tool) -> dict[str, Any]:
    """Return the property map from a tool's input schema if available."""
    schema = getattr(tool, "inputSchema", None) or {}
    return schema.get("properties", {}) or {}


def choose_first_key(schema_keys: set[str], candidates: list[str]) -> str | None:
    """Pick the first candidate key that exists in the schema."""
    for key in candidates:
        if key in schema_keys:
            return key
    return None


def parse_tool_error(exc: Exception) -> dict[str, Any]:
    """Best-effort parse for FastMCP ToolError payloads."""
    raw = str(exc)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {"error": raw}


def format_notion_access_hint(parent_page_id: str, payload: dict[str, Any]) -> str:
    """Create a concise, actionable hint for common Notion integration access errors."""
    details = payload.get("error", "")
    feedback_url = payload.get("feedbackUrl")

    lines = [
        "Notion parent-page access check failed.",
        f"Parent page ID used: {parent_page_id}",
        f"Tool error: {details or '[no details]'}",
        "",
        "Fix in Notion:",
        "1. Open the parent page in Notion.",
        "2. Click Share -> Invite and add the 'Zapier' integration.",
        "3. If this page is inside a teamspace, ensure the integration can access that teamspace.",
        "4. Re-run this script.",
    ]
    if feedback_url:
        lines.append(f"Zapier execution details: {feedback_url}")
    return "\n".join(lines)


def extract_notion_page_id(value: str) -> str | None:
    """
    Extract a Notion page ID from either:
    - a plain 32-char hex string
    - a UUID-style 36-char string with hyphens
    - a Notion URL that includes the page ID
    """
    text = (value or "").strip()
    if not text:
        return None

    # UUID-like ID
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text):
        return text.replace("-", "")

    # Compact ID
    if re.fullmatch(r"[0-9a-fA-F]{32}", text):
        return text

    # ID embedded in URL/path
    match = re.search(r"([0-9a-fA-F]{32})(?:[/?#&]|$)", text)
    if match:
        return match.group(1)

    return None


async def main() -> None:
    # 1) Validate configuration up front for cleaner classroom debugging.
    if not ZAPIER_MCP_URL:
        raise RuntimeError("Missing ZAPIER_MCP_URL in .env")
    if not ZAPIER_MCP_API_KEY:
        raise RuntimeError("Missing ZAPIER_MCP_API_KEY in .env")
    if not NOTION_PARENT_PAGE_ID:
        raise RuntimeError("Missing NOTION_PARENT_PAGE_ID in .env")

    normalized_parent_page_id = extract_notion_page_id(NOTION_PARENT_PAGE_ID)
    if not normalized_parent_page_id:
        raise RuntimeError(
            "NOTION_PARENT_PAGE_ID must be a Notion page ID or a Notion page URL containing a page ID."
        )

    new_page_title = get_new_page_title()

    transport = StreamableHttpTransport(
        ZAPIER_MCP_URL,
        headers={"Authorization": f"Bearer {ZAPIER_MCP_API_KEY}"},
    )
    client = Client(transport=transport)

    print_header("14 - MCP Direct Tool Call")
    print("Pattern: create a new page through MCP, then retrieve and print its web link")

    async with client:
        # 2) Inspect tool schemas first so this script can adapt to real parameter names.
        # Different deployments may expose e.g. page_id vs pageId.
        tools = await client.list_tools()

        create_tool = next((t for t in tools if t.name == "notion_create_page"), None)
        retrieve_tool = next((t for t in tools if t.name == "notion_retrieve_a_page"), None)

        if create_tool is None:
            raise RuntimeError("Tool 'notion_create_page' not found on the MCP server.")
        if retrieve_tool is None:
            raise RuntimeError("Tool 'notion_retrieve_a_page' not found on the MCP server.")

        create_props = get_tool_schema_map(create_tool)
        retrieve_props = get_tool_schema_map(retrieve_tool)

        print_subheader("Detected notion_create_page input fields")
        print(json.dumps(sorted(create_props.keys()), indent=2))

        print_subheader("Detected notion_retrieve_a_page input fields")
        print(json.dumps(sorted(retrieve_props.keys()), indent=2))

        create_keys = set(create_props.keys())
        retrieve_keys = set(retrieve_props.keys())

        # Common Zapier/Notion-style field names
        title_key = choose_first_key(create_keys, ["title", "name"])
        parent_key = choose_first_key(
            create_keys,
            ["page", "page_id", "pageId", "parent_page", "parent_page_id", "parentId"],
        )

        if title_key is None:
            raise RuntimeError("Could not find a title-like field in notion_create_page schema.")
        if parent_key is None:
            raise RuntimeError(
                "Could not find a parent-page field in notion_create_page schema. "
                "Check the printed schema fields above."
            )

        retrieve_page_key = choose_first_key(
            retrieve_keys,
            ["pageId", "page_id", "page", "id"],
        )
        if retrieve_page_key is None:
            raise RuntimeError(
                "Could not find a page-id field in notion_retrieve_a_page schema. "
                "Check the printed schema fields above."
            )

        # 3) Preflight check: verify MCP can access the configured parent page.
        # This catches Notion permission mistakes before we attempt creation.
        print_subheader("Preflight - Verify Parent Page Access")
        parent_check_args = {
            "instructions": "Verify access to this Notion parent page before creating a child page.",
            retrieve_page_key: normalized_parent_page_id,
        }
        print("Tool: notion_retrieve_a_page")
        print("Arguments:")
        print(json.dumps(parent_check_args, indent=2))
        try:
            parent_check_result = await client.call_tool("notion_retrieve_a_page", parent_check_args)
            print_subheader("VISIBLE TOOL RESULT - Parent Page Access")
            print(format_result_content(parent_check_result))
        except ToolError as exc:
            payload = parse_tool_error(exc)
            raise RuntimeError(format_notion_access_hint(normalized_parent_page_id, payload)) from exc

        create_args = {
            "instructions": "Create a new Notion page under the provided parent page.",
            title_key: new_page_title,
            parent_key: normalized_parent_page_id,
        }

        print_subheader("VISIBLE TOOL CALL - Create Page")
        print("Tool: notion_create_page")
        print("Arguments:")
        print(json.dumps(create_args, indent=2))

        try:
            create_result = await client.call_tool("notion_create_page", create_args)
        except ToolError as exc:
            payload = parse_tool_error(exc)
            raise RuntimeError(format_notion_access_hint(normalized_parent_page_id, payload)) from exc

        print_subheader("VISIBLE TOOL RESULT - Create Page")
        raw_create_text = format_result_content(create_result)
        print(raw_create_text)

        parsed_create = try_parse_result_json(create_result)
        page_id = find_first_value(parsed_create, ("page_id", "pageId", "id"))
        page_url = find_first_value(parsed_create, ("url", "public_url"))

        # 4) If create result has no URL, retrieve the page by ID as a second step.
        if not page_url and page_id:
            retrieve_args = {
                "instructions": "Retrieve the newly created Notion page.",
                retrieve_page_key: page_id,
            }

            print_subheader("VISIBLE TOOL CALL - Retrieve Page")
            print("Tool: notion_retrieve_a_page")
            print("Arguments:")
            print(json.dumps(retrieve_args, indent=2))

            retrieve_result = await client.call_tool("notion_retrieve_a_page", retrieve_args)

            print_subheader("VISIBLE TOOL RESULT - Retrieve Page")
            raw_retrieve_text = format_result_content(retrieve_result)
            print(raw_retrieve_text)

            parsed_retrieve = try_parse_result_json(retrieve_result)
            page_url = find_first_value(parsed_retrieve, ("url", "public_url"))
            page_id = page_id or find_first_value(parsed_retrieve, ("page_id", "pageId", "id"))

        print_subheader("Created Page Summary")
        print(f"Page title: {new_page_title}")
        print(f"Page ID: {page_id or '[not found]'}")
        print(f"Page URL: {page_url or '[not found]'}")

        if page_url:
            print_subheader("OPEN THIS LINK IN YOUR BROWSER")
            print(page_url)
        else:
            print_subheader("No page URL found")
            print(
                "The page may still have been created successfully, but the returned payload "
                "did not include a URL. Check the raw tool result above."
            )


if __name__ == "__main__":
    asyncio.run(main())
