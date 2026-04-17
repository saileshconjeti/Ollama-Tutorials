# File name: 11_orchestrator_worker.py
# Purpose: Student-friendly demo of orchestrator-worker with LangGraph.
# Concepts covered: work planning, specialized workers, shared state, synthesis.
# Builds on: 08_prompt_chaining.py, 09_routing.py
# New concept: one planner delegates work to multiple narrow workers
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled,
#                `pip install -r requirements.txt`
# How to run: `python tutorials/module-2-workflow-patterns/11_orchestrator_worker.py`
# What students should observe:
# - the orchestrator emits a structured WorkPlan
# - workers have narrow responsibilities
# - final synthesis merges structured worker outputs into one deliverable
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import os
import operator
from typing import Annotated, List, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from workflow_utils import ask_ollama_structured, print_header, print_subheader, pretty_json


DEFAULT_TOPIC = (
    "Create a 2-week exam prep plan for a student taking Data Structures and DBMS "
    "while also working a part-time job 15 hours/week."
)

# Speed controls (override with env vars if needed).
FAST_MODE = os.getenv("OW_FAST_MODE", "1") == "1"
USE_LLM_ORCHESTRATOR = os.getenv("OW_USE_LLM_ORCHESTRATOR", "0") == "1"
ORCHESTRATOR_MODEL = os.getenv("OW_ORCHESTRATOR_MODEL", "qwen3:0.6b")
WORKER_MODEL = os.getenv("OW_WORKER_MODEL", "qwen3:0.6b")
SYNTHESIS_MODEL = os.getenv("OW_SYNTHESIS_MODEL", "qwen3:0.6b")
MAX_RETRIES = 0 if FAST_MODE else 2


class WorkerTask(BaseModel):
    worker_name: Literal["study_strategy_worker", "schedule_worker", "wellbeing_worker"]
    goal: str
    input_notes: List[str]


class WorkPlan(BaseModel):
    overall_goal: str
    tasks: List[WorkerTask]


class WorkerResult(BaseModel):
    worker_name: str
    key_findings: List[str]
    recommendation: str


class FinalSynthesis(BaseModel):
    decision: str
    rationale: str
    top_actions: List[str]


class WorkflowState(TypedDict, total=False):
    topic: str
    work_plan: dict
    worker_results: Annotated[list[dict], operator.add]
    final_synthesis: dict


def default_work_plan(topic: str) -> dict:
    """Fast deterministic plan to avoid an extra model call."""
    return WorkPlan(
        overall_goal=f"Build a realistic, high-impact study execution plan for: {topic}",
        tasks=[
            WorkerTask(
                worker_name="study_strategy_worker",
                goal="Prioritize what to study first and how to revise efficiently.",
                input_notes=[
                    "Focus on high-weight and high-difficulty topics first.",
                    "Use active recall, practice questions, and quick revision loops.",
                ],
            ),
            WorkerTask(
                worker_name="schedule_worker",
                goal="Create a practical time-blocked plan with class/work constraints.",
                input_notes=[
                    "Account for 15 hours/week part-time job.",
                    "Balance deep-study blocks with revision and buffer time.",
                ],
            ),
            WorkerTask(
                worker_name="wellbeing_worker",
                goal="Keep the plan sustainable and reduce burnout risk.",
                input_notes=[
                    "Protect sleep and short breaks.",
                    "Provide fallback adjustments for overload days.",
                ],
            ),
        ],
    ).model_dump()


def get_worker_task(work_plan: dict, worker_name: str) -> dict:
    """Fetch the worker's own task from the plan for smaller prompts."""
    for item in work_plan.get("tasks", []):
        if item.get("worker_name") == worker_name:
            return item
    return {}


def orchestrator_node(state: WorkflowState) -> WorkflowState:
    """Create a work plan for three specialized workers."""
    if not USE_LLM_ORCHESTRATOR:
        return {"work_plan": default_work_plan(state["topic"]), "worker_results": []}

    plan = ask_ollama_structured(
        user_prompt=f"""
        Create a work plan for exactly three workers:
        - study_strategy_worker
        - schedule_worker
        - wellbeing_worker

        Topic:
        {state["topic"]}
        """,
        schema_model=WorkPlan,
        model=ORCHESTRATOR_MODEL,
        max_retries=MAX_RETRIES,
    )
    return {"work_plan": plan.model_dump(), "worker_results": []}


def study_strategy_worker_node(state: WorkflowState) -> WorkflowState:
    """Design what and how to study for exams."""
    task = get_worker_task(state["work_plan"], "study_strategy_worker")
    result = ask_ollama_structured(
        user_prompt=f"""
        You are the study strategy worker.
        Focus on:
        - prioritizing high-impact topics
        - active recall and practice problems
        - exam-oriented revision strategy

        Your assigned task:
        {task}

        Topic:
        {state["topic"]}
        """,
        schema_model=WorkerResult,
        model=WORKER_MODEL,
        max_retries=MAX_RETRIES,
    )
    return {"worker_results": [result.model_dump()]}


def schedule_worker_node(state: WorkflowState) -> WorkflowState:
    """Create a realistic time plan around constraints."""
    task = get_worker_task(state["work_plan"], "schedule_worker")
    result = ask_ollama_structured(
        user_prompt=f"""
        You are the schedule worker.
        Focus on:
        - realistic daily and weekly time blocks
        - balancing classes, revision, and part-time job hours
        - clear sequencing from now to exam day

        Your assigned task:
        {task}

        Topic:
        {state["topic"]}
        """,
        schema_model=WorkerResult,
        model=WORKER_MODEL,
        max_retries=MAX_RETRIES,
    )
    return {"worker_results": [result.model_dump()]}


def wellbeing_worker_node(state: WorkflowState) -> WorkflowState:
    """Reduce burnout and keep plan sustainable."""
    task = get_worker_task(state["work_plan"], "wellbeing_worker")
    result = ask_ollama_structured(
        user_prompt=f"""
        You are the wellbeing worker.
        Focus on:
        - sleep, breaks, and stress management
        - signs of overload and fallback adjustments
        - staying consistent without burnout

        Your assigned task:
        {task}

        Topic:
        {state["topic"]}
        """,
        schema_model=WorkerResult,
        model=WORKER_MODEL,
        max_retries=MAX_RETRIES,
    )
    return {"worker_results": [result.model_dump()]}


def synthesize_node(state: WorkflowState) -> WorkflowState:
    """Combine all worker outputs into one final synthesis."""
    synthesis = ask_ollama_structured(
        user_prompt=f"""
        Synthesize the worker outputs into one student-ready recommendation.
        Keep it practical, concise, and easy to act on this week.

        Topic:
        {state["topic"]}

        Worker results:
        {state["worker_results"]}
        """,
        schema_model=FinalSynthesis,
        model=SYNTHESIS_MODEL,
        max_retries=MAX_RETRIES,
    )
    return {"final_synthesis": synthesis.model_dump()}


def build_graph():
    """Create a simple orchestrator-worker graph."""
    graph = StateGraph(WorkflowState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("study_strategy_worker", study_strategy_worker_node)
    graph.add_node("schedule_worker", schedule_worker_node)
    graph.add_node("wellbeing_worker", wellbeing_worker_node)
    graph.add_node("synthesize", synthesize_node)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "study_strategy_worker")
    graph.add_edge("orchestrator", "schedule_worker")
    graph.add_edge("orchestrator", "wellbeing_worker")

    graph.add_edge("study_strategy_worker", "synthesize")
    graph.add_edge("schedule_worker", "synthesize")
    graph.add_edge("wellbeing_worker", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


def prompt_for_topic(default_topic: str = DEFAULT_TOPIC) -> str:
    """Ask for a scenario in terminal; fallback to default if empty."""
    print_subheader("INPUT")
    print("Enter a student planning scenario (or press Enter to use default):")
    print(f"Default: {default_topic}")
    try:
        entered = input("\nScenario> ").strip()
    except EOFError:
        entered = ""
    return entered or default_topic


if __name__ == "__main__":
    print_header("11 - ORCHESTRATOR / WORKER")
    print("Builds on: 08_prompt_chaining.py, 09_routing.py")
    print("New concept: a controller delegates work to specialized workers")
    print(
        f"Speed mode: {'FAST' if FAST_MODE else 'FULL'} | "
        f"LLM orchestrator: {'ON' if USE_LLM_ORCHESTRATOR else 'OFF'} | "
        f"worker model: {WORKER_MODEL}"
    )

    app = build_graph()
    topic = prompt_for_topic()
    result = app.invoke({"topic": topic})

    print_subheader("WORK PLAN")
    print(pretty_json(result["work_plan"]))

    print_subheader("WORKER RESULTS")
    for item in result["worker_results"]:
        print(pretty_json(item))

    print_subheader("FINAL SYNTHESIS")
    print(pretty_json(result["final_synthesis"]))
