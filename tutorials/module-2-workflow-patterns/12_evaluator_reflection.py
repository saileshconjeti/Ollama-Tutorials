# File name: 12_evaluator_reflection.py
# Purpose: Demonstrate evaluator-critique-reflection with optional looping.
# Concepts covered: draft generation, structured critique, revision loop, quality control.
# Builds on: 08_prompt_chaining.py, 10_routing.py, 11_orchestrator_worker.py
# New concept: adding explicit quality control to an LLM workflow
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled,
#                `pip install -r requirements.txt`
# How to run: `python 12_evaluator_reflection.py`
# What students should observe:
# - first create a draft
# - then critique it using explicit evaluation criteria
# - revise if needed, with a maximum loop count
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import os
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

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
    task: str
    draft: dict
    critique: dict
    critique_history: Annotated[list[dict], operator.add]
    revised: dict
    revision_history: Annotated[list[dict], operator.add]
    revision_count: int
    final_output: dict


def draft_node(state: WorkflowState) -> WorkflowState:
    """Create the first draft."""
    draft = ask_ollama_structured(
        user_prompt=f"""
        Write a concise executive update.

        Task:
        {state["task"]}
        """,
        schema_model=DraftOutput,
        model=EVALUATOR_MODEL,
        max_retries=MAX_RETRIES,
    )
    return {
        "draft": draft.model_dump(),
        "revision_count": 0,
        "critique_history": [],
        "revision_history": [],
    }


def critique_node(state: WorkflowState) -> WorkflowState:
    """Critique the current draft."""
    current_text = state.get("revised", state["draft"])
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
        model=CRITIQUE_MODEL,
        max_retries=MAX_RETRIES,
    )
    critique_dict = critique.model_dump()
    return {"critique": critique_dict, "critique_history": [critique_dict]}


def revise_node(state: WorkflowState) -> WorkflowState:
    """Revise the draft using critique instructions."""
    current_text = state.get("revised", state["draft"])
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
        model=EVALUATOR_MODEL,
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
    graph.add_conditional_edges(
        "critique",
        should_revise,
        {
            "revise": "revise",
            "finalize": "finalize",
        },
    )
    graph.add_edge("revise", "critique")
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
    print_header("12 - EVALUATOR / CRITIQUE / REFLECTION")
    print("Builds on: 08_prompt_chaining.py, 10_routing.py, 11_orchestrator_worker.py")
    print("New concept: quality control with explicit critique and revision")
    print(
        f"Speed mode: {'FAST' if FAST_MODE else 'FULL'} | "
        f"writer model: {EVALUATOR_MODEL} | critique model: {CRITIQUE_MODEL} | "
        f"min loops: {MIN_REVISIONS} | max loops: {MAX_REVISIONS}"
    )

    app = build_graph()
    task = prompt_for_task()
    result = app.invoke({"task": task})

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
