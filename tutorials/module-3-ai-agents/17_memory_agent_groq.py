# File name: 17_memory_agent.py
# Purpose: Demonstrate an agent with lightweight long-term memory.
# Concepts covered: memory extraction, persistence, personalization.
# Builds on: 16_react_agent_loop.py
# New concept: storing and reusing user preferences across runs
# Prerequisites: `ollama serve` running, `pip install -r requirements.txt`
# How to run: `python tutorials/module-3-ai-agents/17_memory_agent.py`
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import build_provider_parser, get_selected_provider_and_model
from agent_utils import ask_ollama_structured, print_header, print_subheader, pretty_json

MEMORY_PATH = Path("tutorials/module-3-ai-agents/data/agent_memory.json")
DEFAULT_MESSAGE = "Hi, I am Priya. I prefer concise answers with bullet points and practical examples."


class UserMemory(BaseModel):
    # Student note: this is long-term memory stored on disk.
    # It survives across runs, unlike in-memory variables.
    name: str = "student"
    preferences: List[str] = []
    facts: List[str] = []


class MemoryUpdate(BaseModel):
    # Student note: this is a "memory delta", not full memory.
    # We store only new signals extracted from the latest message.
    detected_name: str
    new_preferences: List[str]
    new_facts: List[str]


class AgentReply(BaseModel):
    # Student note: besides the reply text, we also return attribution.
    # `used_memory_items` shows which memory entries actually influenced the response.
    reply: str
    used_memory_items: List[str]


def load_memory() -> UserMemory:
    # Student note: first run usually has no JSON file yet.
    # Returning defaults keeps the app usable from the very first message.
    if not MEMORY_PATH.exists():
        return UserMemory()

    # Student note: pydantic validation keeps file data safe and typed.
    raw = json.loads(MEMORY_PATH.read_text())
    return UserMemory.model_validate(raw)


def build_memory_context(memory: UserMemory) -> str:
    # Student note: we build a human-readable context string so students can
    # inspect exactly what memory is supplied to the reply model call.
    lines: list[str] = [f"name: {memory.name}"]
    lines.append(
        "preferences: "
        + (", ".join(memory.preferences) if memory.preferences else "(none)")
    )
    lines.append("facts: " + (", ".join(memory.facts) if memory.facts else "(none)"))
    return "\n".join(lines)


def save_memory(memory: UserMemory) -> None:
    # Ensure folder exists before writing JSON to disk.
    # Using pretty JSON (`indent=2`) makes the memory file easy to inspect manually.
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(json.dumps(memory.model_dump(), indent=2))


def merge_unique(base: list[str], incoming: list[str], limit: int = 10) -> list[str]:
    # Student note: long-term memory should stay selective.
    # We deduplicate and cap list size to avoid noisy, bloated context.
    merged = list(base)
    for item in incoming:
        cleaned = item.strip()
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:limit]


def detect_memory_updates(
    message: str,
    model: str,
    provider: str | None = None,
) -> MemoryUpdate:
    # Student note: step 1 is "extraction".
    # We convert messy human text into clean fields before writing memory.
    # Student note: structured extraction is safer than regex-only parsing
    # because user messages are varied and natural language is messy.
    return ask_ollama_structured(
        user_prompt=f"""
Extract memory updates from this message.

Message:
{message}

Rules:
- If no name is explicitly provided, set detected_name to "".
- Keep preferences and facts short and concrete.
- Return empty lists if no new items.
""",
        schema_model=MemoryUpdate,
        model=model,
        provider=provider,
    )


def build_reply(
    message: str,
    memory: UserMemory,
    model: str,
    provider: str | None = None,
) -> AgentReply:
    # Student note: step 2 is "generation".
    # The model receives both latest message + stored memory for personalization.
    # Student note: we pass both JSON memory and readable memory context.
    # JSON is machine-friendly, context text is easier for teaching/debugging.
    memory_context = build_memory_context(memory)
    return ask_ollama_structured(
        user_prompt=f"""
You are a personalized study assistant.
Respond using stored user memory and report what memory was used.

Stored memory:
{memory.model_dump_json(indent=2)}

Memory context (used to answer):
{memory_context}

Latest message:
{message}

Guidelines:
- Address the user by name when available.
- Reflect known preferences.
- Keep response useful for course learning.
- In used_memory_items, include only memory items that directly influenced your reply.
""",
        schema_model=AgentReply,
        model=model,
        provider=provider,
    )


def get_message() -> str:
    print_subheader("INPUT")
    print("Enter a message to the memory agent (or press Enter for default)")
    print(f"Default: {DEFAULT_MESSAGE}")
    entered = input("\nMessage> ").strip()
    return entered or DEFAULT_MESSAGE


if __name__ == "__main__":
    parser = build_provider_parser("Run a memory-backed agent with Ollama or Groq.")
    args = parser.parse_args()
    provider = args.provider
    selected_provider, selected_model = get_selected_provider_and_model(provider)

    print_header("17 - MEMORY AGENT")
    print(f"Provider: {selected_provider} | Model in use: {selected_model}")

    # Student note: we track whether memory file existed only for friendly logging.
    # The actual memory object always comes from `load_memory()`.
    memory_exists = MEMORY_PATH.exists()
    memory = load_memory()

    print_subheader("MEMORY LOAD")
    if memory_exists:
        print(f"Loaded existing memory from: {MEMORY_PATH}")
    else:
        print(f"No memory file found at {MEMORY_PATH}; using defaults")

    print_subheader("MEMORY BEFORE")
    print(pretty_json(memory))

    user_message = get_message()
    updates = detect_memory_updates(
        user_message,
        model=selected_model,
        provider=provider,
    )

    # Apply update only when new signal is present.
    # Empty name means "no update", so we preserve existing value.
    if updates.detected_name.strip():
        memory.name = updates.detected_name.strip()
    # Merge extracted preferences/facts into persistent memory.
    memory.preferences = merge_unique(memory.preferences, updates.new_preferences)
    memory.facts = merge_unique(memory.facts, updates.new_facts)

    # Save so next run can reuse this memory.
    save_memory(memory)

    print_subheader("MEMORY UPDATE")
    print(pretty_json(updates))

    print_subheader("MEMORY AFTER")
    print(pretty_json(memory))

    print_subheader("MEMORY CONTEXT FOR REPLY")
    print(build_memory_context(memory))

    reply = build_reply(
        user_message,
        memory,
        model=selected_model,
        provider=provider,
    )
    print_subheader("AGENT REPLY")
    print(reply.reply)

    print_subheader("MEMORY USED IN REPLY")
    print(pretty_json(reply.used_memory_items))
