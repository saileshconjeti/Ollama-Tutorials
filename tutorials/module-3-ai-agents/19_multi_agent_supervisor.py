# File name: 19_multi_agent_supervisor.py
# Purpose: Demonstrate a supervisor coordinating specialized agents.
# Concepts covered: delegation, role specialization, synthesis.
# Builds on: 18_planner_executor_agent.py
# New concept: multi-agent collaboration with a supervisor pattern
# Prerequisites: `ollama serve` running, `pip install -r requirements.txt`
# How to run: `python tutorials/module-3-ai-agents/19_multi_agent_supervisor.py`
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import operator
from typing import Annotated, List, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent_utils import ask_ollama_structured, print_header, print_subheader, pretty_json

DEFAULT_TASK = "Design an AI-agent mini project for students to complete in one week."


class DelegationTask(BaseModel):
    # Student note: each task pairs a worker identity with a concrete objective.
    # This makes delegation explicit and auditable.
    worker: Literal["researcher", "architect", "reviewer"]
    objective: str


class DelegationPlan(BaseModel):
    # Student note: supervisor sets one shared mission and then splits work.
    mission: str
    tasks: List[DelegationTask]


class WorkerOutput(BaseModel):
    # Student note: identical output shape across workers simplifies synthesis.
    worker: str
    findings: List[str]
    recommendation: str


class SupervisorReport(BaseModel):
    # Final synthesis returned to the user.
    final_strategy: str
    milestones: List[str]
    risks: List[str]


class TeamState(TypedDict, total=False):
    # Student note: this is shared team state for all nodes in the graph.
    # `worker_outputs` uses add-merge so parallel workers can append safely.
    # Without this, parallel branches can overwrite each other's data.
    user_task: str
    plan: dict
    worker_outputs: Annotated[list[dict], operator.add]
    report: dict


def plan_node(state: TeamState) -> TeamState:
    # Student note: supervisor first creates assignments before any worker runs.
    # This mirrors real teams: plan first, then parallel execution.
    plan = ask_ollama_structured(
        user_prompt=f"""
Create a delegation plan with exactly these workers:
- researcher
- architect
- reviewer

User task:
{state['user_task']}
""",
        schema_model=DelegationPlan,
    )
    # Student note: initialize `worker_outputs` so branch returns can be merged.
    return {"plan": plan.model_dump(), "worker_outputs": []}


def _task_for(plan: dict, worker_name: str) -> dict:
    # Student note: tiny helper so each worker can fetch only its own task.
    # Fallback keeps the graph robust even if planner misses a worker.
    for item in plan.get("tasks", []):
        if item.get("worker") == worker_name:
            return item
    return {"worker": worker_name, "objective": "Support the mission with your role."}


def researcher_node(state: TeamState) -> TeamState:
    # Worker 1: gathers relevant ideas and evidence.
    # Student note: each worker returns a single-item list because merge is list-add.
    task = _task_for(state["plan"], "researcher")
    out = ask_ollama_structured(
        user_prompt=f"""
You are the researcher agent.
Assigned task:
{task}

Mission:
{state['plan'].get('mission', state['user_task'])}
""",
        schema_model=WorkerOutput,
    )
    return {"worker_outputs": [out.model_dump()]}


def architect_node(state: TeamState) -> TeamState:
    # Worker 2: designs structure and implementation approach.
    # Student note: this role translates ideas into implementable structure.
    task = _task_for(state["plan"], "architect")
    out = ask_ollama_structured(
        user_prompt=f"""
You are the architect agent.
Assigned task:
{task}

Mission:
{state['plan'].get('mission', state['user_task'])}
""",
        schema_model=WorkerOutput,
    )
    return {"worker_outputs": [out.model_dump()]}


def reviewer_node(state: TeamState) -> TeamState:
    # Worker 3: checks gaps, risks, and quality.
    # Student note: reviewer provides critical feedback before final synthesis.
    task = _task_for(state["plan"], "reviewer")
    out = ask_ollama_structured(
        user_prompt=f"""
You are the reviewer agent.
Assigned task:
{task}

Mission:
{state['plan'].get('mission', state['user_task'])}
""",
        schema_model=WorkerOutput,
    )
    return {"worker_outputs": [out.model_dump()]}


def supervisor_node(state: TeamState) -> TeamState:
    # Student note: this is the "manager summary" stage.
    # It combines all worker perspectives into one final strategy.
    # Student note: supervisor receives all branch outputs after they join.
    report = ask_ollama_structured(
        user_prompt=f"""
Synthesize one final strategy from all worker outputs.

Original user task:
{state['user_task']}

Plan:
{state['plan']}

Worker outputs:
{state['worker_outputs']}
""",
        schema_model=SupervisorReport,
    )
    return {"report": report.model_dump()}


def build_graph():
    # Graph topology:
    # START -> planner -> (researcher, architect, reviewer in parallel) -> supervisor -> END
    # Student note: three branches run after planner, then join at supervisor.
    # This demonstrates true parallel delegation in LangGraph.
    graph = StateGraph(TeamState)
    graph.add_node("planner", plan_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("architect", architect_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("supervisor", supervisor_node)

    graph.add_edge(START, "planner")
    # Student note: three outgoing edges from planner create parallel worker branches.
    graph.add_edge("planner", "researcher")
    graph.add_edge("planner", "architect")
    graph.add_edge("planner", "reviewer")
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("architect", "supervisor")
    graph.add_edge("reviewer", "supervisor")
    graph.add_edge("supervisor", END)
    return graph.compile()


def get_task() -> str:
    print_subheader("INPUT")
    print("Enter a multi-agent mission (or press Enter for default)")
    print(f"Default: {DEFAULT_TASK}")
    entered = input("\nMission> ").strip()
    return entered or DEFAULT_TASK


if __name__ == "__main__":
    print_header("19 - MULTI AGENT SUPERVISOR")
    app = build_graph()
    task = get_task()

    # Student note: graph result includes intermediate artifacts (plan + workers)
    # and final synthesis (report), useful for teaching and debugging.
    result = app.invoke({"user_task": task})
    # Result contains plan, merged worker outputs, and supervisor report.

    print_subheader("DELEGATION PLAN")
    print(pretty_json(result["plan"]))

    print_subheader("WORKER OUTPUTS")
    for item in result["worker_outputs"]:
        print(pretty_json(item))

    print_subheader("SUPERVISOR REPORT")
    print(pretty_json(result["report"]))
