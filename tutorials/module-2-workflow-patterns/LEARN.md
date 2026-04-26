# LEARN - Workflow Patterns

Module: **Module 2**

## Theory Goals

By the end of this class, students should be able to:

- explain prompt chaining as a multi-step reasoning workflow
- explain provider-aware workflows (local Ollama vs cloud Groq) using consistent application code
- explain routing as conditional branching to specialized handlers/models
- explain orchestrator-worker delegation with specialized worker roles
- explain evaluator-reflection loops for iterative quality improvement
- explain how tool calling bridges workflow patterns to agentic control loops
- explain MCP as a remote tool provider pattern for agent workflows
- explain schema introspection and argument-key adaptation for robust tool invocation
- explain how to compose structured LLM output with MCP-backed application actions
- inspect and reason about intermediate workflow state

## Concept Map

1. Prompt Chaining (`08_prompt_chaining.py`, `08_prompt_chaining_groq.py`)
- step 1: transform raw notes into structured minutes
- step 2: transform minutes into actionable plan
- each step has validated schema output
- groq variant adds `--provider ollama|groq` while preserving the same chaining structure

2. Routing (`09_routing.py`, `09_routing_groq.py`)
- classify incoming message
- branch to specialized handler
- use route-specific model strategy
- merge structured outputs into final response
- groq variant routes all model nodes through the selected provider model

3. Orchestrator-Worker (`10_orchestrator_worker.py`, `10_orchestrator_worker_groq.py`)
- orchestrator creates a structured work plan
- workers execute narrow responsibilities in parallel graph branches
- synthesis combines worker outputs into one final recommendation
- groq variant keeps the same graph topology with provider-aware structured calls

4. Evaluator-Reflection (`11_evaluator_reflection.py`, `11_evaluator_reflection_groq.py`)
- draft is generated first
- critique evaluates clarity, completeness, actionability, and tone
- revision loop applies feedback with configurable min/max loop counts
- final output is selected after quality checks
- groq variant supports role-aware writer/critique model selection

5. Tool Calling Bridge (`12_tool_calling.py`, `12_tool_calling_groq.py`)
- model proposes a tool call from a provided schema
- application executes the requested tool deterministically
- model consumes tool result and produces final response
- implementation uses `ask_ollama_structured(...)` from `workflow_utils.py`
- groq variant preserves the same tool loop with provider CLI support

6. MCP Tool Discovery (`13_mcp_list_tools.py`)
- connect to an MCP server over authenticated transport
- list available tools and descriptions before execution
- treat discovery as a prerequisite to reliable tool calling

7. Direct MCP Tool Call (`14_mcp_direct_tool_call.py`)
- inspect tool input schemas to detect real parameter names at runtime
- run a preflight parent-page access check before creating resources
- create a Notion page, retrieve metadata, and print shareable URL
- support both Zapier MCP tool modes:
  - legacy per-app tools (`notion_create_page`, `notion_retrieve_a_page`)
  - generic tools (`execute_zapier_read_action` / `execute_zapier_write_action`) with action keys

8. MCP Notion Writer Variants (`15_mcp_qwen_notion_writer.py`, `15_mcp_groq_notion_writer.py`)
- generate structured content (`doc` or `tasks`) with validated schema output
- render model output into markdown for deterministic downstream writing
- create a page and append generated markdown via MCP, then resolve page link
- handle Zapier follow-up create prompts by retrying with explicit defaults to keep runs non-interactive

## Why This Matters

- Reliability: explicit state and schema validation reduce ambiguity
- Control: app code governs execution rather than free-form model behavior
- Scalability: workflows are easier to extend than one giant prompt
- Portability: the same workflow logic can run on local or cloud providers
- Quality: critique-revise loops make improvement explicit and measurable
- Separation of concerns: using a different critique model can reduce self-evaluation bias
- Agent-readiness: tool-calling connects workflow design to app-driven agent loops
- Integration-readiness: MCP connects local workflow code to external SaaS tools (Notion via Zapier)
- Robustness: schema-aware argument mapping reduces brittle connector assumptions

## Files Covered

- `08_prompt_chaining.py`
- `08_prompt_chaining_groq.py`
- `09_routing.py`
- `09_routing_groq.py`
- `10_orchestrator_worker.py`
- `10_orchestrator_worker_groq.py`
- `11_evaluator_reflection.py`
- `11_evaluator_reflection_groq.py`
- `12_tool_calling.py`
- `12_tool_calling_groq.py`
- `13_mcp_list_tools.py`
- `14_mcp_direct_tool_call.py`
- `15_mcp_qwen_notion_writer.py`
- `15_mcp_groq_notion_writer.py`
- `workflow_utils.py`
- root `requirements.txt` (shared by all modules)
