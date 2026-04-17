# LEARN - Workflow Patterns

Module: **Module 2**

## Theory Goals

By the end of this class, students should be able to:

- explain how tool calling creates controlled model-to-code interaction
- explain prompt chaining as a multi-step reasoning workflow
- explain routing as conditional branching to specialized handlers/models
- explain orchestrator-worker delegation with specialized worker roles
- explain evaluator-reflection loops for iterative quality improvement
- inspect and reason about intermediate workflow state

## Concept Map

1. Tool Calling (`07_tool_calling.py`)
- model proposes tool call
- application validates and executes tool
- model receives tool result and finalizes answer

2. Prompt Chaining (`08_prompt_chaining.py`)
- step 1: transform raw notes into structured minutes
- step 2: transform minutes into actionable plan
- each step has validated schema output

3. Routing (`09_routing.py`)
- classify incoming message
- branch to specialized handler
- use route-specific model strategy
- merge structured outputs into final response

4. Orchestrator-Worker (`11_orchestrator_worker.py`)
- orchestrator creates a structured work plan
- workers execute narrow responsibilities in parallel graph branches
- synthesis combines worker outputs into one final recommendation

5. Evaluator-Reflection (`12_evaluator_reflection.py`)
- draft is generated first
- critique evaluates clarity, completeness, actionability, and tone
- revision loop applies feedback with configurable min/max loop counts
- final output is selected after quality checks

## Why This Matters

- Reliability: explicit state and schema validation reduce ambiguity
- Control: app code governs execution rather than free-form model behavior
- Scalability: workflows are easier to extend than one giant prompt
- Quality: critique-revise loops make improvement explicit and measurable
- Separation of concerns: using a different critique model can reduce self-evaluation bias

## Files Covered

- `07_tool_calling.py`
- `08_prompt_chaining.py`
- `09_routing.py`
- `11_orchestrator_worker.py`
- `12_evaluator_reflection.py`
- `workflow_utils.py`
