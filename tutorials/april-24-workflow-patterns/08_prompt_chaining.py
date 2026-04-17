# File name: 08_prompt_chaining.py
# Purpose: Demonstrate prompt chaining for meeting-minutes summarization.
# Concepts covered: multi-step workflows, structured intermediate state, schema validation.
# Builds on: 01_chat.py, 04_structured_output.py
# New concept: prompt chaining with validated intermediate JSON
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled,
#                `pip install -r requirements.txt`
# How to run: `python tutorials/april-24-workflow-patterns/08_prompt_chaining.py`
# What students should observe:
# - Step 1 converts raw notes into meaningful meeting minutes
# - Step 2 turns those minutes into a practical action plan
# - Input is from a text file (uploaded notes)
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from workflow_utils import ask_ollama_structured, print_header, print_subheader


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MINUTES_FILE = SCRIPT_DIR / "sample_meeting_minutes.txt"
DEFAULT_OUTPUT_FILE = "meeting_minutes_output.md"


class MeaningfulMinutes(BaseModel):
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
    overall_goal: str
    actions: List[ActionItem]
    immediate_next_step: str


def read_minutes_file(path_text: str | Path) -> str:
    """Read uploaded minutes from a local text file path."""
    minutes_path = Path(path_text).expanduser()
    return minutes_path.read_text(encoding="utf-8").strip()


def build_minutes_input(cli_file: str | None = None) -> str:
    """Load minutes from a text file only."""
    if cli_file:
        return read_minutes_file(cli_file)

    print_subheader("TEXT FILE INPUT REQUIRED")
    print(f"Press Enter to use default sample file: {DEFAULT_MINUTES_FILE.name}")
    file_path = input("File path to meeting minutes (.txt): ").strip()
    path_to_use = file_path or DEFAULT_MINUTES_FILE
    return read_minutes_file(path_to_use)


def step_1_make_meaningful_minutes(raw_minutes: str) -> MeaningfulMinutes:
    """Step 1: Convert raw notes into polished, meaningful meeting minutes."""
    return ask_ollama_structured(
        user_prompt=f"""
        Convert the raw meeting notes into meaningful, clean meeting minutes.
        Keep it factual and concise.

        Raw notes:
        {raw_minutes}
        """,
        schema_model=MeaningfulMinutes,
    )


def step_2_create_action_plan(minutes: MeaningfulMinutes) -> MeetingActionPlan:
    """Step 2: Create a clear action plan from structured minutes."""
    return ask_ollama_structured(
        user_prompt=f"""
        Build a practical action plan from the meeting minutes below.
        Fill missing due dates as "TBD".

        Minutes JSON:
        {minutes.model_dump_json(indent=2)}
        """,
        schema_model=MeetingActionPlan,
    )


def build_markdown_output(
    minutes: MeaningfulMinutes,
    plan: MeetingActionPlan,
) -> str:
    """Build markdown output for sharing and review."""
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
    parser = argparse.ArgumentParser(
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

    print_header("08 - PROMPT CHAINING")
    print("Builds on: 01_chat.py, 04_structured_output.py")
    print("Scenario: Meeting minutes summarizer + action planner")
    print("Input mode: text file only")
    print("Output mode: markdown file")

    raw_minutes = build_minutes_input(cli_file=args.file)

    meaningful_minutes = step_1_make_meaningful_minutes(raw_minutes)
    action_plan = step_2_create_action_plan(meaningful_minutes)

    markdown_report = build_markdown_output(meaningful_minutes, action_plan)
    saved_path = write_markdown_output(markdown_report, args.output)
    print_subheader("OUTPUT SAVED")
    print(saved_path)
