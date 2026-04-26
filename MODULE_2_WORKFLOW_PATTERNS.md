# Workflow Patterns

Module: **Module 2**

## Learning Materials

- Theory: [LEARN.md](tutorials/module-2-workflow-patterns/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/module-2-workflow-patterns/BUILD.md)

## Setup

Run once at the beginning of class from repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For every new terminal session:

```bash
source .venv/bin/activate
```

## Module Topics

- `08_prompt_chaining.py`: Multi-step prompt chain with structured intermediate state
- `09_routing.py`: Classification-based routing to specialized handlers/LLMs
- `10_orchestrator_worker.py`: One orchestrator delegates to specialized workers and synthesizes outputs
- `11_evaluator_reflection.py`: Critique-revise loop with explicit quality control
- `12_tool_calling.py`: Tool-calling bridge from workflow patterns to agent loops
- `13_mcp_list_tools.py`: Connect to MCP and discover available Zapier tools
- `14_mcp_direct_tool_call.py`: Direct MCP tool invocation to create/retrieve a Notion page with runtime tool-mode compatibility
- `15_mcp_qwen_notion_writer.py`: Qwen-based MCP Notion writer variant
- `15_mcp_groq_notion_writer.py`: Groq-based MCP Notion writer variant (recommended for cloud workflow demos)
- `workflow_utils.py`: Shared helper utilities (`ask_ollama_structured`, printing, JSON fallback parse)

## Run Order

From repo root:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/09_routing.py
python tutorials/module-2-workflow-patterns/10_orchestrator_worker.py
python tutorials/module-2-workflow-patterns/11_evaluator_reflection.py
python tutorials/module-2-workflow-patterns/12_tool_calling.py
python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py
python tutorials/module-2-workflow-patterns/14_mcp_direct_tool_call.py
python tutorials/module-2-workflow-patterns/15_mcp_qwen_notion_writer.py
python tutorials/module-2-workflow-patterns/15_mcp_groq_notion_writer.py
```

For tutorials `13-15`, set these `.env` variables:

```dotenv
ZAPIER_MCP_URL=...
ZAPIER_MCP_API_KEY=...
NOTION_PARENT_PAGE_ID=...
```

Notes for current Zapier MCP behavior:
- Scripts auto-handle both legacy per-app tools (`notion_create_page`, etc.) and generic execute tools (`execute_zapier_read_action` / `execute_zapier_write_action`).
- If `create_page` returns a follow-up confirmation prompt, the scripts auto-retry with explicit defaults so classroom runs remain non-interactive.

## Prompt Chaining Arguments (`08_prompt_chaining.py`)

Optional CLI arguments:

- `--file`: path to input meeting-notes text file
- `--output`: path for generated markdown report

Examples:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
```

## Learning Focus

- Separate model reasoning steps into explicit workflow stages
- Add deterministic control via application code
- Route requests based on classification and inspect graph state
- Use critique-revision loops for measurable output improvement
- Bridge workflow patterns into app-executed tool loops
- Discover and adapt to MCP tool schemas dynamically
- Add robust external-tool preflight checks and permission-aware error handling
- Compose LLM structured output with MCP tools for end-to-end automation
