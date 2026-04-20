"""
15_mcp_qwen_notion_writer.py

Builds on:
- 12_tool_calling.py
- 13_mcp_list_tools.py
- 14_mcp_direct_tool_call.py

New concept:
- use Qwen to generate a brief or task plan
- create a fresh Notion page under a known parent page
- add the generated content into that page through MCP
- print the Notion web link at the end

Why this is the next step:
In 12_tool_calling.py, the tools are local Python functions.
Here, the pattern is the same, but the tool comes from an MCP server.

Pattern:
1. Ask for a topic
2. Choose mode: doc or tasks
3. Generate structured content with Qwen
4. Create a new Notion page under MCP Demo Parent
5. Add the generated markdown to that page
6. Retrieve and print the page URL

Run:
    python tutorials/module-2-workflow-patterns/15_mcp_qwen_notion_writer.py
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from pydantic import BaseModel, Field

from workflow_utils import ask_ollama_structured, pretty_json, print_header, print_subheader

load_dotenv()

ZAPIER_MCP_URL = os.getenv("ZAPIER_MCP_URL", "").strip()
ZAPIER_MCP_API_KEY = os.getenv("ZAPIER_MCP_API_KEY", "").strip()
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "").strip()

DEFAULT_TOPIC = "MCP for local AI assistants"
DEFAULT_MODE = "doc"


# -------------------------------------------------------------------
# Structured schemas
# -------------------------------------------------------------------
# These Pydantic models define the exact JSON shapes we want from Qwen.
# They also make downstream markdown rendering predictable.

class WriterChoice(BaseModel):
    topic: str
    mode: str = Field(description="Either 'doc' or 'tasks'")
    page_title: str


class ResearchBrief(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    next_steps: list[str]


class TaskPlan(BaseModel):
    title: str
    objective: str
    tasks: list[str]
    notes: list[str]


# -------------------------------------------------------------------
# Runtime input
# -------------------------------------------------------------------

def build_default_page_title(topic: str, mode: str) -> str:
    """Build a page title that is unique enough for classroom demos."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M")
    suffix = "Brief" if mode == "doc" else "Tasks"
    return f"{topic} - {suffix} - {timestamp}"


def get_runtime_inputs() -> WriterChoice:
    """Collect topic, mode, and output page title from the terminal."""
    print_subheader("Enter topic")
    print("Press Enter to use the default example.")
    print(f"Default topic: {DEFAULT_TOPIC}\n")

    topic = input("Topic: ").strip()
    if not topic:
        topic = DEFAULT_TOPIC

    print_subheader("Choose mode")
    print("Type 'doc' for a research brief or 'tasks' for a task checklist.")
    mode = input("Mode [doc/tasks]: ").strip().lower()
    if mode not in {"doc", "tasks"}:
        mode = DEFAULT_MODE

    default_page_title = build_default_page_title(topic, mode)

    print_subheader("Enter new Notion page title")
    print("Press Enter to use the generated default.")
    print(f"Default page title: {default_page_title}\n")

    page_title = input("Page title: ").strip()
    if not page_title:
        page_title = default_page_title

    # Keep runtime input structured too, so printing/logging is consistent.
    return WriterChoice(topic=topic, mode=mode, page_title=page_title)


# -------------------------------------------------------------------
# Qwen generation
# -------------------------------------------------------------------

def generate_doc(topic: str) -> ResearchBrief:
    """Generate a short research brief suitable for students."""
    prompt = f"""
Create a short, student-friendly research brief for this topic.

Topic:
{topic}

Requirements:
- Keep it clear and practical
- Make it suitable for classroom use
- Avoid long dense paragraphs
"""
    # ask_ollama_structured enforces schema + validation + retry.
    return ask_ollama_structured(prompt, ResearchBrief)


def generate_tasks(topic: str) -> TaskPlan:
    """Generate a short task checklist suitable for students."""
    prompt = f"""
Create a short student task plan for this topic.

Topic:
{topic}

Requirements:
- Keep the tasks concrete and actionable
- Include a few useful notes
- Make it easy to paste into Notion
"""
    return ask_ollama_structured(prompt, TaskPlan)


def render_doc_markdown(brief: ResearchBrief) -> str:
    """Convert a research brief into markdown."""
    # Build markdown explicitly so students can see model-output -> document mapping.
    lines = [
        f"# {brief.title}",
        "",
        "## Summary",
        brief.summary,
        "",
        "## Key Points",
    ]
    lines.extend([f"- {item}" for item in brief.key_points])

    lines.extend([
        "",
        "## Next Steps",
    ])
    lines.extend([f"- {item}" for item in brief.next_steps])

    return "\n".join(lines)


def render_task_markdown(plan: TaskPlan) -> str:
    """Convert a task plan into markdown."""
    lines = [
        f"# {plan.title}",
        "",
        "## Objective",
        plan.objective,
        "",
        "## Tasks",
    ]
    lines.extend([f"- [ ] {task}" for task in plan.tasks])

    lines.extend([
        "",
        "## Notes",
    ])
    lines.extend([f"- {note}" for note in plan.notes])

    return "\n".join(lines)


# -------------------------------------------------------------------
# MCP helpers
# -------------------------------------------------------------------

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
    """Try to parse the first text content item as JSON."""
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
    """Recursively find the first non-empty string value for any key in keys."""
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
    """Return the input property map for a tool schema."""
    schema = getattr(tool, "inputSchema", None) or {}
    return schema.get("properties", {}) or {}


def choose_first_key(schema_keys: set[str], candidates: list[str]) -> str | None:
    """Pick the first candidate key that exists in the schema."""
    for key in candidates:
        if key in schema_keys:
            return key
    return None


async def get_tool_map(client: Client) -> dict[str, Any]:
    """Load tools once and return a name->tool mapping."""
    # Discover once, reuse many times.
    tools = await client.list_tools()
    return {tool.name: tool for tool in tools}


async def preflight_verify_parent_access(client: Client, tool_map: dict[str, Any]) -> None:
    """Verify that the configured parent page is accessible."""
    retrieve_tool = tool_map.get("notion_retrieve_a_page")
    if retrieve_tool is None:
        raise RuntimeError("Tool 'notion_retrieve_a_page' is not available.")

    retrieve_props = get_tool_schema_map(retrieve_tool)
    retrieve_keys = set(retrieve_props.keys())
    retrieve_page_key = choose_first_key(retrieve_keys, ["pageId", "page_id", "page", "id"])

    if retrieve_page_key is None:
        raise RuntimeError("Could not determine the page-id parameter for notion_retrieve_a_page.")

    args = {
        "instructions": "Verify access to the configured Notion parent page.",
        retrieve_page_key: NOTION_PARENT_PAGE_ID,
    }

    print_subheader("VISIBLE TOOL CALL - Verify Parent Access")
    print("Tool: notion_retrieve_a_page")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool("notion_retrieve_a_page", args)

    print_subheader("VISIBLE TOOL RESULT - Verify Parent Access")
    print(format_result_content(result))


async def create_page_under_parent(
    client: Client,
    tool_map: dict[str, Any],
    page_title: str,
) -> tuple[str | None, str | None]:
    """
    Create a fresh Notion page under the configured parent page.
    Returns (page_id, page_url_if_available).
    """
    create_tool = tool_map.get("notion_create_page")
    if create_tool is None:
        raise RuntimeError("Tool 'notion_create_page' is not available.")

    create_props = get_tool_schema_map(create_tool)
    create_keys = set(create_props.keys())

    title_key = choose_first_key(create_keys, ["title", "name"])
    parent_key = choose_first_key(
        create_keys,
        ["parent_page", "page", "page_id", "pageId", "parent_page_id", "parentId"],
    )

    if title_key is None:
        raise RuntimeError("Could not determine the title parameter for notion_create_page.")
    if parent_key is None:
        raise RuntimeError("Could not determine the parent-page parameter for notion_create_page.")

    # Dynamic key detection keeps this demo robust across schema variations.
    args = {
        "instructions": "Create a new Notion page under the provided parent page.",
        title_key: page_title,
        parent_key: NOTION_PARENT_PAGE_ID,
    }

    print_subheader("VISIBLE TOOL CALL - Create Page")
    print("Tool: notion_create_page")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool("notion_create_page", args)

    print_subheader("VISIBLE TOOL RESULT - Create Page")
    print(format_result_content(result))

    parsed = try_parse_result_json(result)
    page_id = find_first_value(parsed, ("page_id", "pageId", "id"))
    page_url = find_first_value(parsed, ("url", "public_url"))

    return page_id, page_url


async def add_markdown_to_page(
    client: Client,
    tool_map: dict[str, Any],
    page_id: str,
    markdown_text: str,
) -> None:
    """Append generated markdown content to the created page."""
    add_tool = tool_map.get("notion_add_content_to_page")
    if add_tool is None:
        raise RuntimeError("Tool 'notion_add_content_to_page' is not available.")

    add_props = get_tool_schema_map(add_tool)
    add_keys = set(add_props.keys())

    page_key = choose_first_key(add_keys, ["page_id", "pageId", "page", "id"])
    content_key = choose_first_key(add_keys, ["content", "text", "body"])
    format_key = choose_first_key(add_keys, ["content_format", "format"])

    if page_key is None:
        raise RuntimeError("Could not determine the page-id parameter for notion_add_content_to_page.")
    if content_key is None:
        raise RuntimeError("Could not determine the content parameter for notion_add_content_to_page.")

    args = {
        "instructions": "Add markdown content to the specified Notion page.",
        page_key: page_id,
        content_key: markdown_text,
    }
    if format_key is not None:
        args[format_key] = "markdown"

    print_subheader("VISIBLE TOOL CALL - Add Content")
    print("Tool: notion_add_content_to_page")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool("notion_add_content_to_page", args)

    print_subheader("VISIBLE TOOL RESULT - Add Content")
    print(format_result_content(result))


async def retrieve_page_url(
    client: Client,
    tool_map: dict[str, Any],
    page_id: str,
) -> str | None:
    """Retrieve the created page and extract its web URL."""
    retrieve_tool = tool_map.get("notion_retrieve_a_page")
    if retrieve_tool is None:
        raise RuntimeError("Tool 'notion_retrieve_a_page' is not available.")

    retrieve_props = get_tool_schema_map(retrieve_tool)
    retrieve_keys = set(retrieve_props.keys())
    retrieve_page_key = choose_first_key(retrieve_keys, ["pageId", "page_id", "page", "id"])

    if retrieve_page_key is None:
        raise RuntimeError("Could not determine the page-id parameter for notion_retrieve_a_page.")

    args = {
        "instructions": "Retrieve the newly created Notion page.",
        retrieve_page_key: page_id,
    }

    print_subheader("VISIBLE TOOL CALL - Retrieve Page")
    print("Tool: notion_retrieve_a_page")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool("notion_retrieve_a_page", args)

    print_subheader("VISIBLE TOOL RESULT - Retrieve Page")
    print(format_result_content(result))

    parsed = try_parse_result_json(result)
    return find_first_value(parsed, ("url", "public_url"))


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

async def main() -> None:
    # 1) Validate required environment variables before any interactive/model work.
    if not ZAPIER_MCP_URL:
        raise RuntimeError("Missing ZAPIER_MCP_URL in .env")
    if not ZAPIER_MCP_API_KEY:
        raise RuntimeError("Missing ZAPIER_MCP_API_KEY in .env")
    if not NOTION_PARENT_PAGE_ID:
        raise RuntimeError("Missing NOTION_PARENT_PAGE_ID in .env")

    choice = get_runtime_inputs()

    print_header("15 - Qwen + MCP Notion Writer")
    print("Pattern: generate useful content with Qwen, create a fresh Notion page, and write into it")

    print_subheader("Runtime Inputs")
    print(pretty_json(choice))

    # 2) Use LLM + schema based on selected mode.
    if choice.mode == "tasks":
        structured_output = generate_tasks(choice.topic)
        markdown_text = render_task_markdown(structured_output)
    else:
        structured_output = generate_doc(choice.topic)
        markdown_text = render_doc_markdown(structured_output)

    print_subheader("Structured LLM Output")
    print(pretty_json(structured_output))

    print_subheader("Rendered Markdown To Write")
    print(markdown_text)

    transport = StreamableHttpTransport(
        ZAPIER_MCP_URL,
        headers={"Authorization": f"Bearer {ZAPIER_MCP_API_KEY}"},
    )
    client = Client(transport=transport)

    async with client:
        # 3) MCP phase: verify access -> create page -> write markdown -> resolve URL.
        tool_map = await get_tool_map(client)

        await preflight_verify_parent_access(client, tool_map)

        page_id, page_url = await create_page_under_parent(client, tool_map, choice.page_title)

        if not page_id:
            raise RuntimeError(
                "The page appears to have been created, but no page ID was extracted from the result."
            )

        print_subheader("Created Page ID")
        print(page_id)

        await add_markdown_to_page(client, tool_map, page_id, markdown_text)

        if not page_url:
            page_url = await retrieve_page_url(client, tool_map, page_id)

        print_subheader("Done")
        print("The generated content has been written to Notion.")

        print_subheader("New Notion Page Link")
        print(page_url or "[page URL not found]")


if __name__ == "__main__":
    asyncio.run(main())
