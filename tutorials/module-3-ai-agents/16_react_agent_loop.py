# File name: 16_react_agent_loop.py
# Purpose: Show a simple ReAct-style agent loop with explicit tool calls.
# Concepts covered: think-act-observe cycles, bounded loops, tool grounding.
# Builds on: module-2 tool-calling pattern
# New concept: repeated reasoning and tool use until completion
# Prerequisites: `ollama serve` running, `pip install -r requirements.txt`
# How to run: `python tutorials/module-3-ai-agents/16_react_agent_loop.py`
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import re
import time
from typing import Literal

from pydantic import BaseModel

from agent_utils import ask_ollama_structured, print_header, print_subheader, pretty_json

DEFAULT_TASK = "Find two key exam reminders from local notes and also compute 18 + 27."
# Guardrail so the agent cannot loop forever.
MAX_STEPS = 5
STREAM_DELAY = 0.01

# Small local knowledge source used by the tool.
COURSE_NOTES = (
    "Week 5 exam briefing: submit assignment 3 by Friday 11:59 PM; revise sorting, hashing, and SQL joins; "
    "complete 2 mock quizzes before lab day; bring student ID for lab evaluation check-in; "
    "review dynamic programming patterns for coding round; prepare one-page DBMS normalization summary; "
    "office hours for doubt clearing are Wednesday 4-6 PM; attendance is mandatory for Thursday review session; "
    "late assignment penalty is 10 percent per day; focus first on high-weight topics from the rubric."
)


class AgentStep(BaseModel):
    # Student note: each loop returns exactly one "decision object".
    # This is easier to debug than free-form text because fields are predictable.
    thought: str
    action: Literal["search_notes", "math_add", "finish"]
    action_input: str
    final_answer: str


class ToolResult(BaseModel):
    # Student note: we wrap tool output in a schema for consistency.
    # A fixed structure makes it easier to log and feed observations back to the model.
    tool_name: str
    output: str


def search_notes(query: str) -> str:
    # Student note: this tool is intentionally simple and deterministic so
    # classroom runs are reproducible (same input -> same output).
    q = query.lower().strip()
    note_parts = [p.strip() for p in re.split(r"[;,]\s*", COURSE_NOTES) if p.strip()]
    matches = [p for p in note_parts if q in p.lower()]

    # Fallback: match by overlap of query words if phrase match is not found.
    if not matches:
        query_tokens = [w for w in re.findall(r"[a-z0-9]+", q) if len(w) > 2]
        for part in note_parts:
            p_lower = part.lower()
            if any(token in p_lower for token in query_tokens):
                matches.append(part)

    if matches:
        return "; ".join(matches[:3])
    return f"No direct match for '{query}'. Full notes: {COURSE_NOTES}"


def math_add(raw: str) -> str:
    # Student note: tools should validate inputs and fail gracefully.
    # Returning clear error strings helps the agent self-correct in later steps.
    # Parse common classroom input styles like "2+3" or "2,3".
    cleaned = raw.replace(" ", "")
    if "+" in cleaned:
        left, right = cleaned.split("+", maxsplit=1)
    elif "," in cleaned:
        left, right = cleaned.split(",", maxsplit=1)
    else:
        return "ERROR: Use format like 18+27 or 18,27"

    try:
        return str(float(left) + float(right))
    except ValueError:
        return "ERROR: Could not parse numbers for addition."


def run_tool(action: str, action_input: str) -> ToolResult:
    # Student note: the LLM chooses the *intent* (action), but Python executes the tool.
    # This keeps control in code and avoids unsafe direct model execution.
    if action == "search_notes":
        output = search_notes(action_input)
    elif action == "math_add":
        output = math_add(action_input)
    else:
        output = "No tool executed."

    return ToolResult(tool_name=action, output=output)


def build_prompt(user_task: str, trajectory: list[dict]) -> str:
    # Student note: this prompt contains three key ingredients:
    # 1) tool list, 2) rules, 3) trajectory (past observations).
    # Without trajectory, each step behaves like stateless guessing.
    return f"""
You are an agent that can run tools in a loop.

Available tools:
- search_notes: find reminders from local notes. action_input should be a search phrase.
- math_add: add two numbers. action_input format: 18+27
- finish: return final answer and stop.

Rules:
- Choose one action per step.
- Use tools when needed before finishing.
- Keep reasoning concise.

User task:
{user_task}

Current trajectory (previous thoughts/actions/observations):
{trajectory}
"""


def stream_text(label: str, text: str, delay: float = STREAM_DELAY) -> None:
    """
    Tiny streaming helper for classroom demos.
    This is UI streaming (character-by-character print), not token streaming from model API.
    """
    print(f"{label}: ", end="", flush=True)
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def stream_event(step_index: int, phase: str, detail: str) -> None:
    """Readable event stream line for each internal phase."""
    stream_text(f"[step {step_index}] {phase}", detail)


def get_task() -> str:
    print_subheader("INPUT")
    print("Enter an agent task (or press Enter to use default)")
    print(f"Default: {DEFAULT_TASK}")
    entered = input("\nTask> ").strip()
    return entered or DEFAULT_TASK


if __name__ == "__main__":
    print_header("16 - REACT AGENT LOOP")
    task = get_task()

    # Student note: "trajectory" is short-term memory for this single run.
    # We keep prior thoughts/actions/observations so the next step can reason better.
    trajectory: list[dict] = []
    # Student note: this counter powers the "must use at least one tool" guardrail.
    # It teaches that final answers should be evidence-backed.
    tool_calls_made = 0

    # ReAct loop: decide -> act -> observe -> repeat.
    for step_index in range(1, MAX_STEPS + 1):
        print_subheader(f"STEP {step_index} STREAM")
        stream_event(step_index, "status", "Preparing context for the model")
        stream_event(
            step_index,
            "context",
            f"Trajectory items available: {len(trajectory)}",
        )
        stream_event(step_index, "model", "Sending decision request to LLM")

        decision = ask_ollama_structured(
            user_prompt=build_prompt(task, trajectory),
            schema_model=AgentStep,
        )
        stream_event(step_index, "model", "Received structured decision")

        # Stream the key decision fields so students can follow the loop naturally.
        stream_text("Thought", decision.thought)
        stream_text("Action", f"{decision.action} | input: {decision.action_input}")

        # Teaching guardrail: if agent tries to finish too early, force one tool call first.
        if decision.action == "finish" and tool_calls_made == 0:
            stream_event(
                step_index,
                "guardrail",
                "Finish blocked: no tool evidence yet; forcing one tool call for grounding",
            )
            decision.action = "search_notes"
            decision.action_input = "exam reminders"

        if decision.action == "finish":
            # Explicit termination action keeps the loop easy to reason about.
            # The `break` exits the loop immediately and skips remaining iterations.
            print_subheader("FINAL ANSWER")
            stream_text("Answer", decision.final_answer)
            stream_event(step_index, "status", "Loop completed successfully")
            break

        # Execute exactly one tool call from the model's structured decision.
        stream_event(
            step_index,
            "tool",
            f"Dispatching tool '{decision.action}' with input '{decision.action_input}'",
        )
        tool_result = run_tool(decision.action, decision.action_input)
        tool_calls_made += 1
        stream_event(step_index, "tool", f"Tool '{tool_result.tool_name}' returned output")
        stream_text("Observation", tool_result.output)

        # Optional structured snapshot for debugging and teaching.
        print_subheader("STEP SNAPSHOT (JSON)")
        print(pretty_json({"decision": decision, "tool_result": tool_result}))

        trajectory.append(
            {
                # Student note: this dictionary is the "observation history"
                # given back to the model on the next iteration.
                # In ReAct terms, this captures Thought -> Action -> Observation.
                "step": step_index,
                "thought": decision.thought,
                "action": decision.action,
                "action_input": decision.action_input,
                "observation": tool_result.output,
            }
        )
        stream_event(step_index, "memory", f"Trajectory updated to {len(trajectory)} items")
    else:
        # Runs only when loop didn't hit "break" (Python for/else behavior).
        print_subheader("STOPPED")
        print("Reached max steps before finish action. Increase MAX_STEPS if needed.")
