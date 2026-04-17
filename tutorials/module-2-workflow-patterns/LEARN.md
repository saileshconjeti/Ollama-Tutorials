# LEARN - Workflow Patterns

Module: **Module 2**

## Theory Goals

By the end of this class, students should be able to:

- explain how tool calling creates controlled model-to-code interaction
- explain prompt chaining as a multi-step reasoning workflow
- explain routing as conditional branching to specialized handlers/models
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

## Why This Matters

- Reliability: explicit state and schema validation reduce ambiguity
- Control: app code governs execution rather than free-form model behavior
- Scalability: workflows are easier to extend than one giant prompt

## Files Covered

- `07_tool_calling.py`
- `08_prompt_chaining.py`
- `09_routing.py`
- `workflow_utils.py`
