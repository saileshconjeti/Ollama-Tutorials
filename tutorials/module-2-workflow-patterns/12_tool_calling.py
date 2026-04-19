"""
13_tool_use_pattern.py

Builds on:
- 07_tool_calling.py
- 10_routing.py

New concept:
- tool use inside a larger workflow

Why this is the next step:
The model is good at language.
Python tools are good at deterministic actions.
This pattern combines both.

Pattern:
1. Decide whether a tool is needed
2. Build the tool call
3. Execute the tool in Python
4. Produce the final answer

Run:
    python 13_tool_use_pattern.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from workflow_utils import ask_ollama_structured, print_header, print_subheader, pretty_json


# -------------------------------------------------------------------
# Sample local data
# -------------------------------------------------------------------

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

SAMPLE_FILE = DATA_DIR / "sample_note.txt"
if not SAMPLE_FILE.exists():
    SAMPLE_FILE.write_text(
        "Course reminders: submit your project proposal by Friday, "
        "form groups of three, bring your laptop to the lab, "
        "and install Ollama before next week's tutorial."
    )


DEFAULT_QUERY = "Read the local course note and tell me the two most important reminders."


# -------------------------------------------------------------------
# Structured schemas
# -------------------------------------------------------------------

class ToolDecision(BaseModel):
    # Step 1: model decides whether external deterministic execution is needed.
    needs_tool: bool
    tool_name: Literal[
        "calculator_add",
        "calculator_multiply",
        "read_file",
        "count_words",
        "get_day_name",
        "keyword_check",
        "study_time_estimate",
        "none",
    ]
    reason: str


class ToolInvocation(BaseModel):
    # Step 2: model outputs a structured "function call" payload.
    tool_name: Literal[
        "calculator_add",
        "calculator_multiply",
        "read_file",
        "count_words",
        "get_day_name",
        "keyword_check",
        "study_time_estimate",
    ]
    arguments: dict[str, Any]


class ToolResult(BaseModel):
    # Step 3 output: normalized tool execution result for downstream prompting.
    tool_name: str
    output: str


class FinalAnswer(BaseModel):
    # Step 4 output: user-facing answer grounded in tool output.
    answer: str
    used_tool: bool


# -------------------------------------------------------------------
# Tools
# -------------------------------------------------------------------

def calculator_add(a: float, b: float) -> str:
    """Add two numbers."""
    return str(a + b)


def calculator_multiply(a: float, b: float) -> str:
    """Multiply two numbers."""
    return str(a * b)


def read_file(path: str) -> str:
    """Read a local text file."""
    file_path = Path(path)
    if not file_path.exists():
        return f"ERROR: File not found: {path}"
    return file_path.read_text()


def count_words(text: str) -> str:
    """Count the number of words in a text."""
    return str(len(text.split()))


def get_day_name(date_text: str) -> str:
    """Return weekday name for a YYYY-MM-DD date."""
    dt = datetime.strptime(date_text, "%Y-%m-%d")
    return dt.strftime("%A")


def keyword_check(text: str, keyword: str) -> str:
    """Check whether a keyword exists in the text."""
    found = keyword.lower() in text.lower()
    return f"Keyword '{keyword}' found: {found}"


def study_time_estimate(topics: int, minutes_per_topic: int) -> str:
    """Estimate total study time in minutes."""
    total = topics * minutes_per_topic
    return f"{total} minutes"


# -------------------------------------------------------------------
# LLM steps
# -------------------------------------------------------------------

def get_user_query() -> str:
    """Read the query from the terminal. Use a default if empty."""
    print_subheader("Enter a user query")
    print("Press Enter to use the default example.")
    print(f"Default: {DEFAULT_QUERY}\n")

    query = input("User query: ").strip()
    if not query:
        return DEFAULT_QUERY
    return query


def decide_tool(query: str) -> ToolDecision:
    """Ask the model whether a tool is needed."""
    # Keep the decision schema tight so routing stays deterministic in app code.
    prompt = f"""
Decide whether this user request needs a tool.

Available tools:
- calculator_add
- calculator_multiply
- read_file
- count_words
- get_day_name
- keyword_check
- study_time_estimate
- none

User request:
{query}
"""
    return ask_ollama_structured(prompt, ToolDecision)


def build_tool_invocation(query: str, decision: ToolDecision) -> ToolInvocation:
    """Ask the model to construct the tool call."""
    # We constrain arguments per tool so execution can remain safe and predictable.
    prompt = f"""
Create the tool invocation for the chosen tool.

User request:
{query}

Chosen tool:
{decision.tool_name}

Useful local file path if needed:
{str(SAMPLE_FILE)}

Rules:
- For calculator_add, provide arguments: a, b
- For calculator_multiply, provide arguments: a, b
- For read_file, provide argument: path
- For count_words, provide argument: text
- For get_day_name, provide argument: date_text
- For keyword_check, provide arguments: text, keyword
- For study_time_estimate, provide arguments: topics, minutes_per_topic
"""
    return ask_ollama_structured(prompt, ToolInvocation)


def execute_tool(invocation: ToolInvocation) -> ToolResult:
    """Execute the chosen tool and return its result."""
    tool_name = invocation.tool_name
    args = invocation.arguments

    print_subheader("VISIBLE TOOL CALL")
    print(f"Tool selected: {tool_name}")
    print("Arguments:")
    print(pretty_json(args))

    # Parse schema arguments to concrete Python types before calling each tool.
    if tool_name == "calculator_add":
        output = calculator_add(float(args["a"]), float(args["b"]))
    elif tool_name == "calculator_multiply":
        output = calculator_multiply(float(args["a"]), float(args["b"]))
    elif tool_name == "read_file":
        output = read_file(str(args["path"]))
    elif tool_name == "count_words":
        output = count_words(str(args["text"]))
    elif tool_name == "get_day_name":
        output = get_day_name(str(args["date_text"]))
    elif tool_name == "keyword_check":
        output = keyword_check(str(args["text"]), str(args["keyword"]))
    elif tool_name == "study_time_estimate":
        output = study_time_estimate(
            int(args["topics"]),
            int(args["minutes_per_topic"]),
        )
    else:
        output = f"ERROR: Unsupported tool: {tool_name}"

    print_subheader("VISIBLE TOOL RESULT")
    print(output)

    return ToolResult(tool_name=tool_name, output=output)


def create_final_answer(query: str, tool_result: ToolResult) -> FinalAnswer:
    """Ask the model to produce the final user-facing answer."""
    prompt = f"""
Answer the user's request clearly.

User request:
{query}

Tool result:
{tool_result.model_dump_json(indent=2)}
"""
    return ask_ollama_structured(prompt, FinalAnswer)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

if __name__ == "__main__":
    print_header("13 - Tool Use Pattern")
    print("Pattern: let the model decide when to use a tool")
    print("Why it matters: combine language with reliable local actions")

    user_query = get_user_query()

    print_subheader("User Query")
    print(user_query)

    decision = decide_tool(user_query)
    print_subheader("Tool Decision")
    print(pretty_json(decision))

    # Branch: either answer directly or run the tool loop.
    if not decision.needs_tool or decision.tool_name == "none":
        print_subheader("Final")
        print("No tool was needed.")
    else:
        invocation = build_tool_invocation(user_query, decision)
        print_subheader("Tool Invocation")
        print(pretty_json(invocation))

        tool_result = execute_tool(invocation)
        print_subheader("Structured Tool Result")
        print(pretty_json(tool_result))

        final_answer = create_final_answer(user_query, tool_result)
        print_subheader("Final Answer")
        print(pretty_json(final_answer))
