# File name: 08_prompt_chaining_groq.py
# Purpose: Demonstrate prompt chaining for meeting-minutes summarization with switchable provider (Ollama or Groq).
# Concepts covered: multi-step workflows, structured intermediate state, schema validation.
# Builds on: 01_chat_groq.py, 04_structured_output_groq.py
# New concept: prompt chaining with validated intermediate JSON
# Prerequisites: `pip install -r requirements.txt`; for Ollama mode, `ollama serve` and model pulled; for Groq mode, `GROQ_API_KEY` set.
# How to run: `python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider ollama`
# What students should observe:
# - Step 1 converts raw notes into meaningful meeting minutes
# - Step 2 turns those minutes into a practical action plan
# - Input is from a text file (uploaded notes)
# Usage examples:
#   python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider ollama
#   python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider groq
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import build_provider_parser, get_selected_provider_and_model
from workflow_utils import ask_ollama_structured, print_header, print_subheader


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MINUTES_FILE = SCRIPT_DIR / "sample_meeting_minutes.txt"
DEFAULT_OUTPUT_FILE = "meeting_minutes_output.md"


class MeaningfulMinutes(BaseModel):
    # Structured output from chain step 1.
    meeting_title: str
    meeting_purpose: str
    key_decisions: List[str]
    important_updates: List[str]
    open_questions: List[str]


class ActionItem(BaseModel):
    owner: str
    action: str
    due_date: str = Field(description="Use exact date when known, otherwise write 'TBD'")
    priority: str = Field(description="low, medium, or high")


class MeetingActionPlan(BaseModel):
    # Structured output from chain step 2.
    overall_goal: str
    actions: List[ActionItem]
    immediate_next_step: str


def read_minutes_file(path_text: str | Path) -> str:
    """Read uploaded minutes from a local text file path."""
    minutes_path = Path(path_text).expanduser()
    return minutes_path.read_text(encoding="utf-8").strip()


def build_minutes_input(cli_file: str | None = None) -> str:
    """Load minutes from a text file only."""
    # This keeps I/O simple for students: one source of truth is a .txt file.
    if cli_file:
        return read_minutes_file(cli_file)

    print_subheader("TEXT FILE INPUT REQUIRED")
    print(f"Press Enter to use default sample file: {DEFAULT_MINUTES_FILE.name}")
    file_path = input("File path to meeting minutes (.txt): ").strip()
    path_to_use = file_path or DEFAULT_MINUTES_FILE
    return read_minutes_file(path_to_use)


def step_1_make_meaningful_minutes(raw_minutes: str, provider: str | None = None) -> MeaningfulMinutes:
    """Step 1: Convert raw notes into polished, meaningful meeting minutes."""
    return ask_ollama_structured(
        user_prompt=f"""
        Convert the raw meeting notes into meaningful, clean meeting minutes.
        Keep it factual and concise.

        Raw notes:
        {raw_minutes}
        """,
        schema_model=MeaningfulMinutes,
        provider=provider,
    )


def step_2_create_action_plan(minutes: MeaningfulMinutes, provider: str | None = None) -> MeetingActionPlan:
    """Step 2: Create a clear action plan from structured minutes."""
    # Prompt chaining core idea:
    # pass validated JSON from step 1 into step 2.
    return ask_ollama_structured(
        user_prompt=f"""
        Build a practical action plan from the meeting minutes below.
        Fill missing due dates as "TBD".

        Minutes JSON:
        {minutes.model_dump_json(indent=2)}
        """,
        schema_model=MeetingActionPlan,
        provider=provider,
    )


def build_markdown_output(
    minutes: MeaningfulMinutes,
    plan: MeetingActionPlan,
) -> str:
    """Build markdown output for sharing and review."""
    # Convert structured objects into a human-friendly report format.
    key_decisions = "\n".join(f"- {item}" for item in minutes.key_decisions)
    important_updates = "\n".join(f"- {item}" for item in minutes.important_updates)
    open_questions = "\n".join(f"- {item}" for item in minutes.open_questions)
    actions = "\n".join(
        f"- **Owner:** {item.owner} | **Action:** {item.action} | **Due:** {item.due_date} | **Priority:** {item.priority}"
        for item in plan.actions
    )

    return f"""# Meaningful Meeting Minutes

## Meeting Details
- **Meeting Title:** {minutes.meeting_title}
- **Purpose:** {minutes.meeting_purpose}

## Key Decisions
{key_decisions}

## Important Updates
{important_updates}

## Open Questions
{open_questions}

# Action Plan

## Overall Goal
{plan.overall_goal}

## Immediate Next Step
{plan.immediate_next_step}

## Action Items
{actions}
"""


def write_markdown_output(markdown_text: str, output_path: str) -> Path:
    """Write markdown report to disk and return the resolved path."""
    path = Path(output_path).expanduser()
    path.write_text(markdown_text.strip() + "\n", encoding="utf-8")
    return path.resolve()


if __name__ == "__main__":
    parser = build_provider_parser(
        description="Prompt chaining demo: meeting minutes summarizer + action planner."
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a .txt file with meeting notes.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help="Path to the output markdown file.",
    )
    args = parser.parse_args()
    provider = args.provider
    selected_provider, selected_model = get_selected_provider_and_model(provider)

    print_header("08 - PROMPT CHAINING (GROQ/OLLAMA)")
    print("Builds on: 01_chat_groq.py, 04_structured_output_groq.py")
    print("Scenario: Meeting minutes summarizer + action planner")
    print("Input mode: text file only")
    print("Output mode: markdown file")
    print(f"Provider: {selected_provider} | Model: {selected_model}")

    raw_minutes = build_minutes_input(cli_file=args.file)

    # Chain step 1 -> step 2 with typed intermediate state.
    meaningful_minutes = step_1_make_meaningful_minutes(raw_minutes, provider=provider)
    action_plan = step_2_create_action_plan(meaningful_minutes, provider=provider)

    # Final step: persist the chain output for review/sharing.
    markdown_report = build_markdown_output(meaningful_minutes, action_plan)
    saved_path = write_markdown_output(markdown_report, args.output)
    print_subheader("OUTPUT SAVED")
    print(saved_path)
