"""
15_mcp_notion_writer.py

Builds on:
- 12_tool_calling.py
- 13_mcp_list_tools.py
- 14_mcp_direct_tool_call.py

New concept:
- use the selected LLM provider to generate a brief or task plan
- create a fresh Notion page under a known parent page
- add the generated content into that page through MCP
- print the Notion web link at the end

Why this is the next step:
In 12_tool_calling.py, the tools are local Python functions.
Here, the pattern is the same, but the tool comes from an MCP server.

Pattern:
1. Ask for a topic
2. Choose mode: doc or tasks
3. Generate structured content with Ollama or Groq
4. Create a new Notion page under MCP Demo Parent
5. Add the generated markdown to that page
6. Retrieve and print the page URL

Teaching note:
Zapier MCP can expose Notion in two shapes:
- older direct tools such as notion_create_page
- newer generic tools such as execute_zapier_write_action

This file handles both shapes so students can focus on the workflow:
LLM output -> MCP tool call -> external app result.

Run:
    python tutorials/module-2-workflow-patterns/15_mcp_notion_writer.py --provider ollama
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import build_provider_parser, get_selected_provider_and_model
from workflow_utils import (
    ask_ollama_structured,
    pretty_json,
    print_actionable_error,
    print_ascii_tree,
    print_header,
    print_step,
    print_subheader,
)

load_dotenv(override=True)

ZAPIER_MCP_URL = os.getenv("ZAPIER_MCP_URL", "").strip()
ZAPIER_MCP_API_KEY = os.getenv("ZAPIER_MCP_API_KEY", "").strip()
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "").strip()

DEFAULT_TOPIC = "MCP for local AI assistants"
DEFAULT_MODE = "doc"
DEFAULT_OLLAMA_WRITER_MODEL = os.getenv("OLLAMA_CHAT_MODEL", os.getenv("OLLAMA_MODEL", "qwen3:4b"))
LEGACY_ZAPIER_MCP_URL = "https://mcp.zapier.com/api/v1/connect"


def validate_zapier_mcp_config() -> None:
    """Check the MCP connection settings before students get deep into the demo."""
    if not ZAPIER_MCP_URL:
        print_actionable_error(
            "ZAPIER_MCP_URL is missing in .env.",
            "The MCP client needs the Zapier server URL before it can write generated content to Notion.",
            [
                "Open Zapier MCP and copy the Streamable HTTP server URL.",
                "Add ZAPIER_MCP_URL=your_server_url to .env.",
                "Re-run this script.",
            ],
        )
        raise SystemExit(1)
    has_url_token = "token=" in ZAPIER_MCP_URL
    if not ZAPIER_MCP_API_KEY and not has_url_token:
        print_actionable_error(
            "ZAPIER_MCP_API_KEY is missing.",
            "The MCP server requires authentication before it will accept Notion tool calls.",
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


# -------------------------------------------------------------------
# Structured schemas
# -------------------------------------------------------------------
# Pydantic models act like a contract with the LLM.
# Instead of asking for "some text", we ask for fields we can trust later.

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
    """Build a readable page title that will not collide during repeated demos."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M")
    suffix = "Brief" if mode == "doc" else "Tasks"
    return f"{topic} - {suffix} - {timestamp}"


def get_runtime_inputs() -> WriterChoice:
    """Collect the few choices that should change from one run to the next."""
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

    # Use the same structured-data habit for human input that we use for model output.
    return WriterChoice(topic=topic, mode=mode, page_title=page_title)


# -------------------------------------------------------------------
# LLM generation
# -------------------------------------------------------------------

def generate_doc(topic: str, model: str, provider: str | None = None) -> ResearchBrief:
    """Ask the selected model for a research brief that matches ResearchBrief."""
    prompt = f"""
Create a short, student-friendly research brief for this topic.

Topic:
{topic}

Requirements:
- Keep it clear and practical
- Make it suitable for classroom use
- Avoid long dense paragraphs
"""
    # ask_ollama_structured handles provider calls, schema validation, and retries.
    return ask_ollama_structured(
        prompt,
        ResearchBrief,
        model=model,
        provider=provider,
    )


def generate_tasks(topic: str, model: str, provider: str | None = None) -> TaskPlan:
    """Ask the selected model for a checklist that matches TaskPlan."""
    prompt = f"""
Create a short student task plan for this topic.

Topic:
{topic}

Requirements:
- Keep the tasks concrete and actionable
- Include a few useful notes
- Make it easy to paste into Notion
"""
    return ask_ollama_structured(
        prompt,
        TaskPlan,
        model=model,
        provider=provider,
    )


def render_doc_markdown(brief: ResearchBrief) -> str:
    """Turn validated model data into the markdown we will send to Notion."""
    # Keep this mapping simple: each schema field becomes one visible section.
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
    """Turn validated task data into Notion-friendly markdown."""
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
    """Convert MCP result chunks into text we can print for students."""
    chunks = []
    for item in result.content:
        if hasattr(item, "text"):
            chunks.append(item.text)
        else:
            chunks.append(str(item))
    return "\n".join(chunks) if chunks else "[no text output returned]"


def try_parse_result_json(result) -> Any:
    """Parse JSON from an MCP result when the tool returns structured text."""
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
    """Search nested tool output for values like page_id or page_url."""
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
    """Return the input properties advertised by one MCP tool."""
    schema = getattr(tool, "inputSchema", None) or {}
    return schema.get("properties", {}) or {}


def choose_first_key(schema_keys: set[str], candidates: list[str]) -> str | None:
    """Pick the first parameter name that this MCP server actually supports."""
    for key in candidates:
        if key in schema_keys:
            return key
    return None


def extract_notion_page_id(value: str) -> str | None:
    """
    Accept either a raw Notion page ID or a copied Notion URL.

    Extract a Notion page ID from:
    - plain 32-char hex
    - UUID with hyphens
    - Notion URL containing the ID
    """
    text = (value or "").strip()
    if not text:
        return None

    if re.fullmatch(r"[0-9a-fA-F]{32}", text):
        return text
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text):
        return text.replace("-", "")

    match = re.search(r"([0-9a-fA-F]{32})(?:[/?#&]|$)", text)
    if match:
        return match.group(1)
    return None


def normalize_tool_name(name: str) -> str:
    """Make tool names comparable even if separators or casing differ."""
    return re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")


def find_tool_by_name(tools: list[Any], expected_name: str) -> Any | None:
    """Find a tool by exact name first, then by normalized name."""
    expected_norm = normalize_tool_name(expected_name)
    for tool in tools:
        if getattr(tool, "name", "") == expected_name:
            return tool
    for tool in tools:
        if normalize_tool_name(getattr(tool, "name", "")) == expected_norm:
            return tool
    return None


def parse_enabled_actions_payload(payload: Any) -> list[dict[str, Any]]:
    """Pull enabled Notion action records out of Zapier's generic action list."""
    if isinstance(payload, list):
        actions: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, dict) and isinstance(item.get("actions"), list):
                for action in item["actions"]:
                    if isinstance(action, dict):
                        actions.append(action)
        return actions
    return []


def choose_zapier_notion_action(
    actions: list[dict[str, Any]],
    preferred_keys: list[str],
    name_tokens: tuple[str, ...],
    preferred_tool: str | None = None,
) -> dict[str, Any] | None:
    """Choose the Notion action that best matches the workflow step we need."""
    for key in preferred_keys:
        for action in actions:
            if action.get("key") == key:
                return action

    candidates: list[dict[str, Any]] = []
    for action in actions:
        key = str(action.get("key", "")).lower()
        name = str(action.get("name", "")).lower()
        searchable = f"{key} {name}"
        if all(token in searchable for token in name_tokens):
            candidates.append(action)

    if preferred_tool:
        for action in candidates:
            if action.get("tool") == preferred_tool:
                return action
    return candidates[0] if candidates else None


def parse_action_param_keys(payload: Any) -> set[str]:
    """Read the parameter names Zapier expects for one enabled action."""
    keys: set[str] = set()
    for action in parse_enabled_actions_payload(payload):
        for param in action.get("params", []):
            if isinstance(param, dict):
                key = param.get("key")
                if isinstance(key, str) and key.strip():
                    keys.add(key.strip())
    return keys


async def get_tool_map(client: Client) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Discover the MCP tools available in this Zapier server.

    Returns:
    - tool name -> tool metadata
    - runtime config for create/retrieve/add-content calls

    The runtime config hides small Zapier differences from the rest of the file.
    After this function, the main workflow can call "create page" without caring
    whether this server uses legacy notion_* tools or generic execute_zapier_* tools.
    """
    tools = await client.list_tools()
    tool_map = {tool.name: tool for tool in tools}

    # First try the simpler teaching path: direct Notion tools with clear names.
    create_tool = find_tool_by_name(tools, "notion_create_page")
    retrieve_tool = find_tool_by_name(tools, "notion_retrieve_a_page")
    add_tool = find_tool_by_name(tools, "notion_add_content_to_page")

    if create_tool and retrieve_tool and add_tool:
        create_props = get_tool_schema_map(create_tool)
        retrieve_props = get_tool_schema_map(retrieve_tool)
        add_props = get_tool_schema_map(add_tool)

        create_keys = set(create_props.keys())
        retrieve_keys = set(retrieve_props.keys())
        add_keys = set(add_props.keys())

        # MCP schemas tell us the exact argument names to send.
        # This keeps the demo resilient when providers use title vs name, etc.
        title_key = choose_first_key(create_keys, ["title", "name"])
        parent_key = choose_first_key(
            create_keys,
            ["parent_page", "page", "page_id", "pageId", "parent_page_id", "parentId"],
        )
        retrieve_page_key = choose_first_key(retrieve_keys, ["pageId", "page_id", "page", "id"])
        add_page_key = choose_first_key(add_keys, ["page_id", "pageId", "page", "id"])
        content_key = choose_first_key(add_keys, ["content", "text", "body"])
        format_key = choose_first_key(add_keys, ["content_format", "format"])

        if not all([title_key, parent_key, retrieve_page_key, add_page_key, content_key]):
            raise RuntimeError(
                "Legacy Notion tools were found, but required parameter keys are missing in schemas."
            )

        return tool_map, {
            "mode": "legacy",
            "create_tool_name": str(create_tool.name),
            "retrieve_tool_name": str(retrieve_tool.name),
            "add_tool_name": str(add_tool.name),
            "title_key": title_key,
            "parent_key": parent_key,
            "retrieve_page_key": retrieve_page_key,
            "add_page_key": add_page_key,
            "content_key": content_key,
            "format_key": format_key,
        }

    # If direct Notion tools are not present, use Zapier's newer generic tools.
    # In this mode we first list enabled Notion actions, then execute by action key.
    has_generic_tools = {
        "list_enabled_zapier_actions",
        "execute_zapier_write_action",
    }.issubset(set(tool_map.keys()))
    if not has_generic_tools:
        raise RuntimeError(
            "No compatible Notion MCP tool mode detected. Expected either legacy notion_* tools "
            "or generic execute_zapier_* tools."
        )

    # Ask Zapier which Notion actions are enabled for this MCP server.
    actions_result = await client.call_tool("list_enabled_zapier_actions", {"app": "notion"})
    actions_payload = try_parse_result_json(actions_result)
    notion_actions = parse_enabled_actions_payload(actions_payload)
    if not notion_actions:
        raise RuntimeError(
            "No enabled Notion actions found in Zapier MCP. Enable Notion actions and retry."
        )

    # Resolve the three app-level operations this lesson needs.
    create_action = choose_zapier_notion_action(
        notion_actions,
        preferred_keys=["create_page", "notion_create_page"],
        name_tokens=("create", "page"),
        preferred_tool="execute_zapier_write_action",
    )
    retrieve_action = choose_zapier_notion_action(
        notion_actions,
        preferred_keys=[
            "get_page_or_database_item_by_id",
            "ae_38538_notion_retrieve_a_page",
            "notion_retrieve_a_page",
        ],
        name_tokens=("page", "id"),
        preferred_tool="execute_zapier_read_action",
    ) or choose_zapier_notion_action(
        notion_actions,
        preferred_keys=[],
        name_tokens=("retrieve", "page"),
    )
    add_action = choose_zapier_notion_action(
        notion_actions,
        preferred_keys=["page_content", "notion_add_content_to_page", "add_content_to_page"],
        name_tokens=("content", "page"),
        preferred_tool="execute_zapier_write_action",
    )

    if create_action is None or retrieve_action is None or add_action is None:
        raise RuntimeError(
            "Could not resolve required Notion actions (create/retrieve/add-content) in Zapier MCP."
        )

    create_action_key = str(create_action["key"])
    retrieve_action_key = str(retrieve_action["key"])
    add_action_key = str(add_action["key"])

    # Fetch each action schema so we can send the exact parameter names Zapier wants.
    create_schema_result = await client.call_tool(
        "list_enabled_zapier_actions", {"app": "notion", "action": create_action_key}
    )
    retrieve_schema_result = await client.call_tool(
        "list_enabled_zapier_actions", {"app": "notion", "action": retrieve_action_key}
    )
    add_schema_result = await client.call_tool(
        "list_enabled_zapier_actions", {"app": "notion", "action": add_action_key}
    )

    create_param_keys = parse_action_param_keys(try_parse_result_json(create_schema_result))
    retrieve_param_keys = parse_action_param_keys(try_parse_result_json(retrieve_schema_result))
    add_param_keys = parse_action_param_keys(try_parse_result_json(add_schema_result))

    title_key = choose_first_key(create_param_keys, ["title", "name"])
    parent_key = choose_first_key(
        create_param_keys,
        ["parent_page", "page", "page_id", "pageId", "parent_page_id", "parentId"],
    )
    retrieve_page_key = choose_first_key(retrieve_param_keys, ["page_id", "pageId", "page", "id"])
    add_page_key = choose_first_key(add_param_keys, ["page_id", "pageId", "page", "id"])
    content_key = choose_first_key(add_param_keys, ["content", "text", "body"])
    format_key = choose_first_key(add_param_keys, ["content_format", "format"])

    if not all([title_key, parent_key, retrieve_page_key, add_page_key, content_key]):
        raise RuntimeError(
            "Generic Zapier Notion actions were found, but required parameter keys are missing."
        )

    return tool_map, {
        "mode": "generic",
        "create_tool_name": str(create_action.get("tool", "execute_zapier_write_action")),
        "retrieve_tool_name": str(retrieve_action.get("tool", "execute_zapier_read_action")),
        "add_tool_name": str(add_action.get("tool", "execute_zapier_write_action")),
        "create_action_key": create_action_key,
        "retrieve_action_key": retrieve_action_key,
        "add_action_key": add_action_key,
        "title_key": title_key,
        "parent_key": parent_key,
        "retrieve_page_key": retrieve_page_key,
        "add_page_key": add_page_key,
        "content_key": content_key,
        "format_key": format_key,
    }


async def preflight_verify_parent_access(
    client: Client,
    runtime: dict[str, Any],
    parent_page_id: str,
) -> None:
    """Call Notion once before writing so setup problems appear early."""
    retrieve_page_key = runtime["retrieve_page_key"]
    retrieve_tool_name = runtime["retrieve_tool_name"]

    # Generic Zapier calls wrap action inputs inside app/action/params.
    # Legacy Notion tools receive their inputs directly.
    if runtime["mode"] == "generic":
        args = {
            "app": "notion",
            "action": runtime["retrieve_action_key"],
            "instructions": "Verify access to the configured Notion parent page.",
            "output": "Return page id and page url.",
            "params": {retrieve_page_key: parent_page_id},
        }
    else:
        args = {
            "instructions": "Verify access to the configured Notion parent page.",
            retrieve_page_key: parent_page_id,
        }

    print_subheader("VISIBLE TOOL CALL - Verify Parent Access")
    print(f"Tool: {retrieve_tool_name}")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool(retrieve_tool_name, args)

    print_subheader("VISIBLE TOOL RESULT - Verify Parent Access")
    print(format_result_content(result))


async def create_page_under_parent(
    client: Client,
    runtime: dict[str, Any],
    parent_page_id: str,
    page_title: str,
) -> tuple[str | None, str | None]:
    """
    Create a fresh Notion page under the configured parent page.

    This is the first write action in the lesson. We print both the tool call and
    the result so students can see exactly what crossed the MCP boundary.

    Returns (page_id, page_url_if_available).
    """
    create_tool_name = runtime["create_tool_name"]
    title_key = runtime["title_key"]
    parent_key = runtime["parent_key"]

    # Build arguments in the shape required by the discovered runtime mode.
    if runtime["mode"] == "generic":
        args = {
            "app": "notion",
            "action": runtime["create_action_key"],
            "instructions": "Create a new Notion page under the provided parent page.",
            "output": "Return the created page id and page url.",
            "params": {
                title_key: page_title,
                parent_key: parent_page_id,
            },
        }
    else:
        args = {
            "instructions": "Create a new Notion page under the provided parent page.",
            title_key: page_title,
            parent_key: parent_page_id,
        }

    print_subheader("VISIBLE TOOL CALL - Create Page")
    print(f"Tool: {create_tool_name}")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool(create_tool_name, args)

    print_subheader("VISIBLE TOOL RESULT - Create Page")
    print(format_result_content(result))

    parsed = try_parse_result_json(result)
    page_id = find_first_value(parsed, ("page_id", "pageId", "id"))
    page_url = find_first_value(parsed, ("page_url", "url", "public_url"))

    # Some generic Zapier actions ask a follow-up question instead of executing.
    # For a classroom script, retry with explicit defaults so the run stays smooth.
    if runtime["mode"] == "generic" and not page_id:
        follow_up = find_first_value(parsed, ("followUpQuestion",))
        if follow_up:
            print_subheader("Auto-Resolve Follow-Up")
            print("Zapier requested extra confirmation. Retrying create with explicit defaults.")

            retry_args = {
                **args,
                "instructions": (
                    "Create the page now using only provided required parameters. "
                    "Do not ask follow-up questions. "
                    "Use no icon, no cover, and no initial body content."
                ),
            }

            print_subheader("VISIBLE TOOL CALL - Create Page (Retry)")
            print(f"Tool: {create_tool_name}")
            print("Arguments:")
            print(json.dumps(retry_args, indent=2))

            retry_result = await client.call_tool(create_tool_name, retry_args)

            print_subheader("VISIBLE TOOL RESULT - Create Page (Retry)")
            print(format_result_content(retry_result))

            parsed = try_parse_result_json(retry_result)
            page_id = find_first_value(parsed, ("page_id", "pageId", "id"))
            page_url = find_first_value(parsed, ("page_url", "url", "public_url"))

    return page_id, page_url


async def add_markdown_to_page(
    client: Client,
    runtime: dict[str, Any],
    page_id: str,
    markdown_text: str,
) -> None:
    """Append the generated markdown to the page created in the previous step."""
    add_tool_name = runtime["add_tool_name"]
    page_key = runtime["add_page_key"]
    content_key = runtime["content_key"]
    format_key = runtime["format_key"]

    if runtime["mode"] == "generic":
        params: dict[str, Any] = {
            page_key: page_id,
            content_key: markdown_text,
        }
        if format_key:
            params[format_key] = "markdown"

        args = {
            "app": "notion",
            "action": runtime["add_action_key"],
            "instructions": "Add markdown content to the specified Notion page.",
            "output": "Return success status for content append.",
            "params": params,
        }
    else:
        args = {
            "instructions": "Add markdown content to the specified Notion page.",
            page_key: page_id,
            content_key: markdown_text,
        }
        if format_key is not None:
            args[format_key] = "markdown"

    print_subheader("VISIBLE TOOL CALL - Add Content")
    print(f"Tool: {add_tool_name}")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool(add_tool_name, args)

    print_subheader("VISIBLE TOOL RESULT - Add Content")
    print(format_result_content(result))


async def retrieve_page_url(
    client: Client,
    runtime: dict[str, Any],
    page_id: str,
) -> str | None:
    """Retrieve the created page when the create call did not include a URL."""
    retrieve_tool_name = runtime["retrieve_tool_name"]
    retrieve_page_key = runtime["retrieve_page_key"]

    if runtime["mode"] == "generic":
        args = {
            "app": "notion",
            "action": runtime["retrieve_action_key"],
            "instructions": "Retrieve the newly created Notion page.",
            "output": "Return page id and page url.",
            "params": {retrieve_page_key: page_id},
        }
    else:
        args = {
            "instructions": "Retrieve the newly created Notion page.",
            retrieve_page_key: page_id,
        }

    print_subheader("VISIBLE TOOL CALL - Retrieve Page")
    print(f"Tool: {retrieve_tool_name}")
    print("Arguments:")
    print(json.dumps(args, indent=2))

    result = await client.call_tool(retrieve_tool_name, args)

    print_subheader("VISIBLE TOOL RESULT - Retrieve Page")
    print(format_result_content(result))

    parsed = try_parse_result_json(result)
    return find_first_value(parsed, ("page_url", "url", "public_url"))


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

async def main() -> None:
    parser = build_provider_parser("Generate content and write it to Notion through MCP.")
    args = parser.parse_args()
    provider = args.provider
    selected_provider, selected_model = get_selected_provider_and_model(provider)
    writer_model = selected_model if selected_provider == "groq" else DEFAULT_OLLAMA_WRITER_MODEL

    # Step 1: Validate setup before asking for input or spending tokens.
    validate_zapier_mcp_config()
    if not NOTION_PARENT_PAGE_ID:
        print_actionable_error(
            "NOTION_PARENT_PAGE_ID is missing in .env.",
            "The demo creates a new Notion child page and needs a parent page location.",
            [
                "Copy the parent Notion page URL or page ID.",
                "Add NOTION_PARENT_PAGE_ID=your_page_id_or_url to .env.",
                "Share that Notion page with the Zapier integration.",
            ],
        )
        raise SystemExit(1)
    normalized_parent_page_id = extract_notion_page_id(NOTION_PARENT_PAGE_ID)
    if not normalized_parent_page_id:
        raise RuntimeError(
            "NOTION_PARENT_PAGE_ID must be a Notion page ID or a Notion page URL containing a page ID."
        )

    choice = get_runtime_inputs()

    print_header("15 - MCP NOTION WRITER")
    print("What this demonstrates: an LLM creates structured content, then MCP writes that content into an external app.")
    print_step(1, "Inspecting LLM-to-MCP flow")
    print_ascii_tree(
        """
        Topic + Mode
            |
            v
        LLM Structured Output
            |
            v
        Render Markdown
            |
            v
        MCP Create Notion Page
            |
            v
        MCP Add Markdown Content
            |
            v
        Notion Page URL
        """
    )
    print_step(2, "Checking provider, model, and runtime inputs")
    print(f"Provider: {selected_provider} | Model: {writer_model}")

    print_subheader("Runtime Inputs")
    print(pretty_json(choice))

    # Step 2: Generate structured content, then render that structure as markdown.
    print_step(3, "Generating structured content with the selected LLM")
    if choice.mode == "tasks":
        structured_output = generate_tasks(choice.topic, model=writer_model, provider=provider)
        markdown_text = render_task_markdown(structured_output)
    else:
        structured_output = generate_doc(choice.topic, model=writer_model, provider=provider)
        markdown_text = render_doc_markdown(structured_output)

    print_subheader("Structured LLM Output")
    print(pretty_json(structured_output))

    print_subheader("Rendered Markdown To Write")
    print(markdown_text)

    headers = {"Authorization": f"Bearer {ZAPIER_MCP_API_KEY}"} if ZAPIER_MCP_API_KEY else {}
    transport = StreamableHttpTransport(ZAPIER_MCP_URL, headers=headers)
    client = Client(transport=transport)

    async with client:
        # Step 3: MCP phase: verify access -> create page -> write markdown -> resolve URL.
        print_step(4, "Discovering Notion MCP tools")
        _tool_map, runtime = await get_tool_map(client)

        print_subheader("Notion MCP Runtime Mode")
        print(runtime["mode"])

        print_step(5, "Verifying parent page access")
        await preflight_verify_parent_access(client, runtime, normalized_parent_page_id)

        print_step(6, "Creating Notion page")
        page_id, page_url = await create_page_under_parent(
            client, runtime, normalized_parent_page_id, choice.page_title
        )

        if not page_id:
            raise RuntimeError(
                "The page appears to have been created, but no page ID was extracted from the result."
            )

        print_subheader("Created Page ID")
        print(page_id)

        print_step(7, "Adding generated markdown to Notion")
        await add_markdown_to_page(client, runtime, page_id, markdown_text)

        if not page_url:
            print_step(8, "Retrieving page URL")
            page_url = await retrieve_page_url(client, runtime, page_id)

        print_subheader("Done")
        print("The generated content has been written to Notion.")

        print_subheader("New Notion Page Link")
        print(page_url or "[page URL not found]")
        print_step(9, "What to observe")
        print("The LLM produced content, but all external side effects happened through explicit MCP tool calls.")


if __name__ == "__main__":
    asyncio.run(main())
