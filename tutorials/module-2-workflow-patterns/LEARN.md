# LEARN - Workflow Patterns

Module: **Module 2**

## Theory Goals

By the end of this class, students should be able to:

- explain prompt chaining as a multi-step reasoning workflow
- explain routing as conditional branching to specialized handlers/models
- explain orchestrator-worker delegation with specialized worker roles
- explain evaluator-reflection loops for iterative quality improvement
- explain how tool calling bridges workflow patterns to agentic control loops
- inspect and reason about intermediate workflow state

## Concept Map

1. Prompt Chaining (`08_prompt_chaining.py`)
- step 1: transform raw notes into structured minutes
- step 2: transform minutes into actionable plan
- each step has validated schema output

2. Routing (`09_routing.py`)
- classify incoming message
- branch to specialized handler
- use route-specific model strategy
- merge structured outputs into final response

3. Orchestrator-Worker (`11_orchestrator_worker.py`)
- orchestrator creates a structured work plan
- workers execute narrow responsibilities in parallel graph branches
- synthesis combines worker outputs into one final recommendation

4. Evaluator-Reflection (`12_evaluator_reflection.py`)
- draft is generated first
- critique evaluates clarity, completeness, actionability, and tone
- revision loop applies feedback with configurable min/max loop counts
- final output is selected after quality checks

5. Tool Calling Bridge (`13_tool_calling.py`)
- model proposes a tool call from a provided schema
- application executes the requested tool deterministically
- model consumes tool result and produces final response

## Why This Matters

- Reliability: explicit state and schema validation reduce ambiguity
- Control: app code governs execution rather than free-form model behavior
- Scalability: workflows are easier to extend than one giant prompt
- Quality: critique-revise loops make improvement explicit and measurable
- Separation of concerns: using a different critique model can reduce self-evaluation bias
- Agent-readiness: tool-calling connects workflow design to app-driven agent loops

## Files Covered

- `08_prompt_chaining.py`
- `09_routing.py`
- `11_orchestrator_worker.py`
- `12_evaluator_reflection.py`
- `13_tool_calling.py`
- `workflow_utils.py`
