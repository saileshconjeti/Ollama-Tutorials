# File name: 09_routing.py
# Purpose: Student-friendly demo of customer review monitoring with LangGraph.
# Concepts covered: classification, branching, explicit routes, graph state.
# Builds on: 04_structured_output.py, 08_prompt_chaining.py
# New concept: route one message to different LLM handlers
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled,
#                `pip install -r requirements.txt`
# How to run: `python tutorials/module-2-workflow-patterns/09_routing.py`
# What students should observe:
# - a classifier emits a structured RouteDecision
# - the graph routes the review to a specialized handler
# - each handler can use a different LLM
# - the final answer is built from routed structured state
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from workflow_utils import ask_ollama_structured, print_header, print_subheader, pretty_json


DEFAULT_REVIEW = (
    "I love the dashboard layout, but after yesterday's update the checkout page freezes "
    "every time I try to apply a coupon."
)
TRIAGE_MODEL = "qwen3:4b"

# Demo setup: route-specific models. Override with environment variables in class if needed.
BUG_MODEL = "qwen3:4b"
FEATURE_MODEL = "qwen3:4b"
PRAISE_MODEL = "qwen3:4b"


class RouteDecision(BaseModel):
    # Classifier output used for branching.
    category: Literal["bug_report", "feature_request", "praise_or_general_feedback"]
    confidence: float
    rationale: str


class HandlerOutput(BaseModel):
    category: str
    summary: str
    priority: Literal["low", "medium", "high"]
    recommended_action: str
    owner_team: str
    response_message: str
    model_used: str


class WorkflowState(TypedDict, total=False):
    # LangGraph shared state keys passed between nodes.
    user_message: str
    route_decision: dict
    handler_output: dict
    final_answer: str


def classify_node(state: WorkflowState) -> WorkflowState:
    """Classify a customer review into one of three support routes."""
    # First step in graph: produce a strict route label.
    decision = ask_ollama_structured(
        user_prompt=f"""
        Classify the message into one of:
        - bug_report
        - feature_request
        - praise_or_general_feedback

        Message:
        {state["user_message"]}
        """,
        schema_model=RouteDecision,
        model=TRIAGE_MODEL,
    )
    return {"route_decision": decision.model_dump()}


def bug_handler_node(state: WorkflowState) -> WorkflowState:
    """Handle bug reports with the bug-focused model."""
    output = ask_ollama_structured(
        user_prompt=f"""
        You are the bug triage assistant for customer reviews.
        Produce a clear internal summary and a short customer-facing response.

        Customer review:
        {state["user_message"]}

        Route decision:
        {state["route_decision"]}
        """,
        schema_model=HandlerOutput,
        model=BUG_MODEL,
    )
    payload = output.model_dump()
    payload["model_used"] = BUG_MODEL
    return {"handler_output": payload}


def feature_handler_node(state: WorkflowState) -> WorkflowState:
    """Handle feature requests with the feature-focused model."""
    output = ask_ollama_structured(
        user_prompt=f"""
        You are the product feedback assistant for feature requests.
        Produce a clear internal summary and a short customer-facing response.

        Customer review:
        {state["user_message"]}

        Route decision:
        {state["route_decision"]}
        """,
        schema_model=HandlerOutput,
        model=FEATURE_MODEL,
    )
    payload = output.model_dump()
    payload["model_used"] = FEATURE_MODEL
    return {"handler_output": payload}


def praise_handler_node(state: WorkflowState) -> WorkflowState:
    """Handle praise/general feedback with the feedback-focused model."""
    output = ask_ollama_structured(
        user_prompt=f"""
        You are the customer experience assistant for praise and general feedback.
        Produce a clear internal summary and a short customer-facing response.

        Customer review:
        {state["user_message"]}

        Route decision:
        {state["route_decision"]}
        """,
        schema_model=HandlerOutput,
        model=PRAISE_MODEL,
    )
    payload = output.model_dump()
    payload["model_used"] = PRAISE_MODEL
    return {"handler_output": payload}


def final_node(state: WorkflowState) -> WorkflowState:
    """Create a human-facing answer from structured downstream state."""
    # Final node formats internal structured data for an operator-friendly view.
    route = state["route_decision"]
    output = state["handler_output"]

    final_answer = (
        f"Route selected: {route['category']} (confidence={route['confidence']:.2f})\n\n"
        f"Model used: {output['model_used']}\n"
        f"Summary: {output['summary']}\n"
        f"Priority: {output['priority']}\n"
        f"Recommended action: {output['recommended_action']}\n"
        f"Owner team: {output['owner_team']}\n\n"
        f"Suggested customer response:\n{output['response_message']}"
    )
    return {"final_answer": final_answer}


def choose_route(state: WorkflowState) -> str:
    """Map RouteDecision to the next node name."""
    # This function drives conditional edges in the graph.
    category = state["route_decision"]["category"]
    if category == "bug_report":
        return "bug_handler"
    if category == "feature_request":
        return "feature_handler"
    return "praise_handler"


def build_graph():
    """Create the customer-review routing graph."""
    graph = StateGraph(WorkflowState)
    graph.add_node("classify", classify_node)
    graph.add_node("bug_handler", bug_handler_node)
    graph.add_node("feature_handler", feature_handler_node)
    graph.add_node("praise_handler", praise_handler_node)
    graph.add_node("final", final_node)

    graph.add_edge(START, "classify")
    # Route dynamically based on classifier output.
    graph.add_conditional_edges(
        "classify",
        choose_route,
        {
            "bug_handler": "bug_handler",
            "feature_handler": "feature_handler",
            "praise_handler": "praise_handler",
        },
    )
    graph.add_edge("bug_handler", "final")
    graph.add_edge("feature_handler", "final")
    graph.add_edge("praise_handler", "final")
    graph.add_edge("final", END)

    return graph.compile()


def prompt_for_review(default_review: str = DEFAULT_REVIEW) -> str:
    """Ask for a review in the terminal; use a default if left blank."""
    print_subheader("INPUT")
    print("Paste a customer review (or press Enter to use the default):")
    print(f"Default: {default_review}")
    try:
        entered = input("\nCustomer review> ").strip()
    except EOFError:
        entered = ""
    return entered or default_review


if __name__ == "__main__":
    print_header("09 - CUSTOMER REVIEW ROUTING")
    print("Builds on: 04_structured_output.py, 08_prompt_chaining.py")
    print("New concept: route one review to different LLM handlers")

    app = build_graph()
    user_review = prompt_for_review()
    # Single invoke call executes classify -> chosen handler -> final.
    result = app.invoke({"user_message": user_review})

    print_subheader("ROUTE DECISION")
    print(pretty_json(result["route_decision"]))

    print_subheader("HANDLER OUTPUT")
    print(pretty_json(result["handler_output"]))

    print_subheader("FINAL HUMAN-FACING ANSWER")
    print(result["final_answer"])
