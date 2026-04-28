# File name: 18_planner_executor_agent.py
# Purpose: Demonstrate a planner -> multi-agent executor pattern with LangGraph.
# Concepts covered: planning, role-based execution, graph state transitions.
# Builds on: module-2 orchestrator-worker and evaluator loops
# New concept: planner assigns role-specific steps, dispatcher routes to specialized agents
# Prerequisites: `ollama serve` running, `pip install -r requirements.txt`
# How to run: `python tutorials/module-3-ai-agents/18_planner_executor_agent.py`
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import build_provider_parser, get_selected_provider_and_model
from agent_utils import ask_ollama_structured, print_header, print_subheader, pretty_json

DEFAULT_GOAL = (
    "Create a 7-day revision plan for machine learning basics before an internal exam."
)

AgentRole = Literal["researcher", "designer", "coach"]


class PlanStep(BaseModel):
    # Student note: each step has BOTH "what to do" and "who should do it".
    # That role assignment is what enables intelligent routing later.
    step_title: str
    objective: str
    role: AgentRole


class Plan(BaseModel):
    # Student note: planner output includes both sequence (`steps`)
    # and quality target (`success_criteria`) for downstream agents.
    goal: str
    steps: List[PlanStep]
    success_criteria: List[str]


class StepExecution(BaseModel):
    # Student note: this enforces a common contract across specialist roles.
    # Consistent schema makes aggregation and review straightforward.
    step_summary: str
    key_points: List[str]
    concrete_actions: List[str]
    handoff_notes: str
    status: Literal["completed", "needs_followup"]


class FinalReport(BaseModel):
    # Student note: reviewer compresses full execution history into actionable guidance.
    summary: str
    what_to_do_today: List[str]
    checkpoints: List[str]


class AgentState(TypedDict, total=False):
    # Student note: this dictionary is the shared "whiteboard" for all nodes.
    # Every node reads from it and can return partial updates to it.
    goal: str
    plan: dict
    step_index: int
    step_outputs: List[dict]

    # Dispatcher-managed fields for current step.
    active_step_title: str
    active_step_objective: str
    active_step_role: AgentRole

    final_report: dict
    provider: str
    model: str


def planner_node(state: AgentState) -> AgentState:
    # Node 1: create an ordered role-based plan.
    # Student note: planning is separate from execution so each stage stays focused.
    plan = ask_ollama_structured(
        user_prompt=f"""
Create a concise execution plan for this goal:
{state['goal']}

Rules:
- Produce exactly 4 steps.
- Use each specialist role at least once: researcher, designer, coach.
- Keep step objectives concrete and classroom friendly.
- Steps must be ordered and build on prior outputs.
""",
        schema_model=Plan,
        model=state["model"],
        provider=state["provider"],
    )

    plan_dict = plan.model_dump()

    print_subheader("PLANNER OUTPUT")
    print(pretty_json(plan_dict))

    # Student note: initialize loop cursor (`step_index`) and empty execution log.
    return {"plan": plan_dict, "step_index": 0, "step_outputs": []}


def dispatch_node(state: AgentState) -> AgentState:
    # Student note: dispatcher selects the current step and exposes it in
    # normalized `active_*` keys so routing logic stays simple.
    idx = state["step_index"]
    steps = state["plan"]["steps"]

    # Student note: returning empty dict means "no state change".
    # The router still decides where control goes next.
    if idx >= len(steps):
        return {}

    current_step = steps[idx]
    return {
        "active_step_title": current_step["step_title"],
        "active_step_objective": current_step["objective"],
        "active_step_role": current_step["role"],
    }


def route_from_dispatch(state: AgentState) -> str:
    # Student note: router decides "which node runs next".
    # If all steps are done, control moves to reviewer.
    idx = state["step_index"]
    total = len(state["plan"]["steps"])

    # Student note: when cursor reaches total steps, execution phase is done.
    if idx >= total:
        return "reviewer"
    return state["active_step_role"]


def _run_specialist(state: AgentState, role: AgentRole, role_instruction: str) -> AgentState:
    # Student note: one reusable function powers all specialist agents.
    # Only role + instruction changes, reducing duplicate code.
    idx = state["step_index"]
    total = len(state["plan"]["steps"])

    # Student note: each specialist gets:
    # 1) goal, 2) success criteria, 3) current step, 4) prior outputs for context.
    execution = ask_ollama_structured(
        system_prompt=role_instruction,
        user_prompt=f"""
Goal:
{state['goal']}

Plan success criteria:
{state['plan']['success_criteria']}

Current assigned step ({idx + 1}/{total}):
Title: {state['active_step_title']}
Objective: {state['active_step_objective']}
Assigned role: {role}

Completed step outputs so far:
{state['step_outputs']}
""",
        schema_model=StepExecution,
        model=state["model"],
        provider=state["provider"],
    )

    output = {
        "step_number": idx + 1,
        "step_title": state["active_step_title"],
        "objective": state["active_step_objective"],
        "role": role,
        "execution": execution.model_dump(),
    }

    # Student note: copy + append avoids mutating state in-place.
    # Returning new state is clearer for graph reasoning and debugging.
    outputs = list(state["step_outputs"])
    outputs.append(output)

    # Print each agent output immediately for classroom visibility.
    print_subheader(f"AGENT OUTPUT - STEP {idx + 1} ({role.upper()})")
    print(pretty_json(output))

    return {
        "step_outputs": outputs,
        "step_index": idx + 1,
    }


def researcher_node(state: AgentState) -> AgentState:
    return _run_specialist(
        state,
        role="researcher",
        role_instruction=(
            "You are the Researcher agent. Focus on factual grounding, key concepts, "
            "and exam-relevant content extraction. Return practical and concise outputs."
        ),
    )


def designer_node(state: AgentState) -> AgentState:
    return _run_specialist(
        state,
        role="designer",
        role_instruction=(
            "You are the Designer agent. Convert ideas into structured plans, timelines, "
            "and learner-friendly formats. Emphasize clarity and sequencing."
        ),
    )


def coach_node(state: AgentState) -> AgentState:
    return _run_specialist(
        state,
        role="coach",
        role_instruction=(
            "You are the Coach agent. Focus on motivation, daily execution, and "
            "risk mitigation. Provide concrete and supportive next actions."
        ),
    )


def reviewer_node(state: AgentState) -> AgentState:
    # Final node: synthesize full run into one student-facing report.
    # Student note: reviewer does not run tools; it summarizes planner + all step outputs.
    report = ask_ollama_structured(
        user_prompt=f"""
Create a final student-facing report from this run.

Goal:
{state['goal']}

Planner output:
{state['plan']}

Specialist outputs in sequence:
{state['step_outputs']}
""",
        schema_model=FinalReport,
        model=state["model"],
        provider=state["provider"],
    )
    return {"final_report": report.model_dump()}


def build_graph():
    # Graph topology:
    # START -> planner -> dispatch -> specialist -> dispatch ... -> reviewer -> END
    # Student note: this creates a "looping graph" where dispatch keeps routing
    # until every planned step is executed.
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("dispatch", dispatch_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("designer", designer_node)
    graph.add_node("coach", coach_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "dispatch")

    # Student note: conditional edges implement dynamic routing by role.
    graph.add_conditional_edges(
        "dispatch",
        route_from_dispatch,
        {
            "researcher": "researcher",
            "designer": "designer",
            "coach": "coach",
            "reviewer": "reviewer",
        },
    )

    graph.add_edge("researcher", "dispatch")
    graph.add_edge("designer", "dispatch")
    graph.add_edge("coach", "dispatch")

    graph.add_edge("reviewer", END)
    return graph.compile()


def get_goal() -> str:
    print_subheader("INPUT")
    print("Enter planning goal (or press Enter for default)")
    print(f"Default: {DEFAULT_GOAL}")
    entered = input("\nGoal> ").strip()
    return entered or DEFAULT_GOAL


if __name__ == "__main__":
    parser = build_provider_parser("Run planner-executor graph with Ollama or Groq.")
    args = parser.parse_args()
    provider = args.provider
    selected_provider, selected_model = get_selected_provider_and_model(provider)

    print_header("18 - PLANNER -> MULTI AGENT EXECUTOR")
    print(f"Provider: {selected_provider} | Model in use: {selected_model}")
    app = build_graph()
    goal = get_goal()

    # Student note: one `invoke` call executes all node transitions until END.
    result = app.invoke(
        {
            "goal": goal,
            "provider": selected_provider,
            "model": selected_model,
        }
    )

    print_subheader("FINAL REPORT")
    print(pretty_json(result["final_report"]))
