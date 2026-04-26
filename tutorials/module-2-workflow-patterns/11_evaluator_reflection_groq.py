# File name: 11_evaluator_reflection_groq.py
# Purpose: Demonstrate evaluator-critique-reflection with optional looping and switchable provider (Ollama or Groq).
# Concepts covered: draft generation, structured critique, revision loop, quality control.
# Builds on: 08_prompt_chaining_groq.py, 09_routing_groq.py, 10_orchestrator_worker_groq.py
# New concept: adding explicit quality control to an LLM workflow
# Prerequisites: `pip install -r requirements.txt`; for Ollama mode, `ollama serve` and model pulled; for Groq mode, `GROQ_API_KEY` set.
# How to run: `python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider ollama`
# What students should observe:
# - first create a draft
# - then critique it using explicit evaluation criteria
# - revise if needed, with a maximum loop count
# Usage examples:
#   python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider ollama
#   python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider groq
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import os
import operator
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import build_provider_parser, get_selected_provider_and_model
from workflow_utils import ask_ollama_structured, print_header, print_subheader, pretty_json


DEFAULT_TASK = "Write a short executive update about a Generative and Agentic AI class project."
MAX_REVISIONS = int(os.getenv("ER_MAX_REVISIONS", "4"))
MIN_REVISIONS = int(os.getenv("ER_MIN_REVISIONS", "1"))
FAST_MODE = os.getenv("ER_FAST_MODE", "0") == "1"
EVALUATOR_MODEL = os.getenv("ER_MODEL", "qwen3:0.6b")
CRITIQUE_MODEL = os.getenv("ER_CRITIQUE_MODEL", "qwen2.5:0.5b")
MAX_RETRIES = 0 if FAST_MODE else 2


class DraftOutput(BaseModel):
    title: str
    body: str


class CritiqueResult(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    missing_items: list[str]
    revision_instructions: list[str]
    needs_revision: bool


class RevisedOutput(BaseModel):
    title: str
    body: str


class WorkflowState(TypedDict, total=False):
    # State captures both latest artifacts and full loop history.
    task: str
    provider: str | None
    active_writer_model: str
    active_critique_model: str
    draft: dict
    critique: dict
    critique_history: Annotated[list[dict], operator.add]
    revised: dict
    revision_history: Annotated[list[dict], operator.add]
    revision_count: int
    final_output: dict


def resolve_node_model(state: WorkflowState, role: Literal["writer", "critique"], default_model: str) -> str:
    """
    Resolve model for each node.
    In Groq mode, use CLI-selected model for all LLM nodes.
    In Ollama mode, keep the node-specific defaults/env overrides.
    """
    if state.get("provider") == "groq":
        if role == "critique":
            return state.get("active_critique_model", default_model)
        return state.get("active_writer_model", default_model)
    return default_model


def draft_node(state: WorkflowState) -> WorkflowState:
    """Create the first draft."""
    model_for_node = resolve_node_model(state, "writer", EVALUATOR_MODEL)
    draft = ask_ollama_structured(
        user_prompt=f"""
        Write a concise executive update.

        Task:
        {state["task"]}
        """,
        schema_model=DraftOutput,
        model=model_for_node,
        provider=state.get("provider"),
        max_retries=MAX_RETRIES,
    )
    return {
        "draft": draft.model_dump(),
        # Loop counters/history are initialized once at draft stage.
        "revision_count": 0,
        "critique_history": [],
        "revision_history": [],
    }


def critique_node(state: WorkflowState) -> WorkflowState:
    """Critique the current draft."""
    # After the first loop, critique the revised draft instead of the original.
    current_text = state.get("revised", state["draft"])
    model_for_node = resolve_node_model(state, "critique", CRITIQUE_MODEL)
    critique = ask_ollama_structured(
        user_prompt=f"""
        Evaluate the draft below for:
        - clarity
        - completeness
        - actionability
        - executive tone

        Be strict. In executive updates, mark needs_revision=true if any item is
        vague, missing concrete outcome/impact, or lacks next actions.

        Output rules:
        - include at least 1 weakness when quality is not strong
        - include missing_items for anything important not stated
        - set needs_revision=true whenever weaknesses or missing_items are non-empty

        Draft:
        {current_text}
        """,
        schema_model=CritiqueResult,
        model=model_for_node,
        provider=state.get("provider"),
        max_retries=MAX_RETRIES,
    )
    critique_dict = critique.model_dump()
    return {"critique": critique_dict, "critique_history": [critique_dict]}


def revise_node(state: WorkflowState) -> WorkflowState:
    """Revise the draft using critique instructions."""
    # Revision node applies explicit critique feedback as constraints.
    current_text = state.get("revised", state["draft"])
    model_for_node = resolve_node_model(state, "writer", EVALUATOR_MODEL)
    revised = ask_ollama_structured(
        user_prompt=f"""
        Revise the draft using the critique below.
        Keep executive tone and improve specificity.
        Include concise outcome/impact and clear next actions.
        Apply all revision_instructions directly.

        Draft:
        {current_text}

        Critique:
        {state["critique"]}
        """,
        schema_model=RevisedOutput,
        model=model_for_node,
        provider=state.get("provider"),
        max_retries=MAX_RETRIES,
    )
    return {
        "revised": revised.model_dump(),
        "revision_history": [revised.model_dump()],
        "revision_count": state["revision_count"] + 1,
    }


def finalize_node(state: WorkflowState) -> WorkflowState:
    """Choose the best available output as final."""
    final_output = state.get("revised", state["draft"])
    return {"final_output": final_output}


def should_revise(state: WorkflowState) -> str:
    """Decide whether to revise again or finalize."""
    critique = state["critique"]
    model_says_revise = bool(critique.get("needs_revision"))
    has_feedback = bool(
        critique.get("weaknesses") or critique.get("missing_items") or critique.get("revision_instructions")
    )
    revision_count = state["revision_count"]

    # MIN_REVISIONS guarantees students can observe at least one loop.
    force_demo_loop = revision_count < MIN_REVISIONS
    should_continue = (model_says_revise or has_feedback or force_demo_loop) and revision_count < MAX_REVISIONS

    if should_continue:
        return "revise"
    return "finalize"


def build_graph():
    """Build the evaluator-reflection loop graph."""
    graph = StateGraph(WorkflowState)
    graph.add_node("draft", draft_node)
    graph.add_node("critique", critique_node)
    graph.add_node("revise", revise_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "draft")
    graph.add_edge("draft", "critique")
    # This conditional edge is the core evaluator/reflection control point.
    graph.add_conditional_edges(
        "critique",
        should_revise,
        {
            "revise": "revise",
            "finalize": "finalize",
        },
    )
    graph.add_edge("revise", "critique")
    # Exit only when quality is acceptable or max loops reached.
    graph.add_edge("finalize", END)

    return graph.compile()


def prompt_for_task(default_task: str = DEFAULT_TASK) -> str:
    """Ask for a writing task in terminal; fallback to default if empty."""
    print_subheader("INPUT")
    print("Enter an executive-update task (or press Enter to use default):")
    print(f"Default: {default_task}")
    try:
        entered = input("\nTask> ").strip()
    except EOFError:
        entered = ""
    return entered or default_task


if __name__ == "__main__":
    parser = build_provider_parser("Run evaluator-critique-reflection workflow with Ollama or Groq.")
    args = parser.parse_args()
    provider = args.provider
    selected_provider, selected_model = get_selected_provider_and_model(provider)
    if selected_provider == "groq":
        # Optional override lets critique use a different Groq model.
        active_writer_model = selected_model
        active_critique_model = os.getenv("ER_GROQ_CRITIQUE_MODEL", selected_model)
    else:
        active_writer_model = EVALUATOR_MODEL
        active_critique_model = CRITIQUE_MODEL

    print_header("11 - EVALUATOR / CRITIQUE / REFLECTION (GROQ/OLLAMA)")
    print("Builds on: 08_prompt_chaining_groq.py, 09_routing_groq.py, 10_orchestrator_worker_groq.py")
    print("New concept: quality control with explicit critique and revision")
    print(
        f"Speed mode: {'FAST' if FAST_MODE else 'FULL'} | "
        f"writer model: {active_writer_model} | critique model: {active_critique_model} | "
        f"min loops: {MIN_REVISIONS} | max loops: {MAX_REVISIONS}"
    )
    print(f"Provider: {selected_provider}")

    app = build_graph()
    task = prompt_for_task()
    result = app.invoke(
        {
            "task": task,
            "provider": selected_provider,
            "active_writer_model": active_writer_model,
            "active_critique_model": active_critique_model,
        }
    )

    print_subheader("INITIAL DRAFT")
    print(pretty_json(result["draft"]))

    print_subheader("LAST CRITIQUE")
    print(pretty_json(result["critique"]))

    if "revised" in result:
        print_subheader("REVISED OUTPUT")
        print(pretty_json(result["revised"]))

    print_subheader("LOOP SUMMARY")
    print(f"Total revisions performed: {result.get('revision_count', 0)}")
    print(f"Total critiques captured: {len(result.get('critique_history', []))}")

    print_subheader("FINAL OUTPUT")
    print(pretty_json(result["final_output"]))
