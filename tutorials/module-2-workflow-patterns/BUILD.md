# BUILD - Workflow Patterns

Module: **Module 2**

## Prerequisites

- `ollama serve` is running
- Python virtual environment is active
- dependencies installed from repo root: `python -m pip install -r requirements.txt`
- models available:
  - `qwen3:0.6b`
  - `qwen2.5:0.5b`
  - `qwen3:4b` (default helper model via `OLLAMA_CHAT_MODEL`)
- MCP tutorials `13-15` also require in `.env`:
  - `ZAPIER_MCP_URL`
  - `ZAPIER_MCP_API_KEY`
  - `NOTION_PARENT_PAGE_ID`

## Create Your `.env` File (Do Not Commit)

Create a `.env` file at the repository root and add:

```dotenv
ZAPIER_MCP_URL=https://mcp.zapier.com/api/v1/connect
ZAPIER_MCP_API_KEY=your_zapier_mcp_api_key
NOTION_PARENT_PAGE_ID=your_notion_parent_page_id_or_url
OLLAMA_CHAT_MODEL=qwen3:4b
```

Notes:
- Keep real keys only in local `.env`; do not commit this file.
- `.gitignore` excludes `.env` and `.env.*` so secrets are not pushed.
- `NOTION_PARENT_PAGE_ID` can be either a Notion page ID or full page URL.

## Environment Setup

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

## Step-by-Step Execution

Run from repository root.

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/09_routing.py
python tutorials/module-2-workflow-patterns/10_orchestrator_worker.py
python tutorials/module-2-workflow-patterns/11_evaluator_reflection.py
python tutorials/module-2-workflow-patterns/12_tool_calling.py
python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py
python tutorials/module-2-workflow-patterns/14_mcp_direct_tool_call.py
python tutorials/module-2-workflow-patterns/15_mcp_qwen_notion_writer.py
```

## Prompt Chaining CLI Arguments (`08_prompt_chaining.py`)

- `--file`: input `.txt` minutes file
- `--output`: output `.md` report path

Examples:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
```

## Suggested Routing Demo Inputs (`09_routing.py`)

- Bug report: "Checkout freezes when I apply a coupon."
- Feature request: "Please add bulk invoice export."
- Praise/general feedback: "Onboarding was smooth and support was excellent."

## Orchestrator-Worker Demo Controls (`10_orchestrator_worker.py`)

- input is interactive (press Enter to use default topic)
- optional env vars:
  - `OW_FAST_MODE=1` (default) for faster runs
  - `OW_USE_LLM_ORCHESTRATOR=0` (default) for deterministic plan
  - `OW_ORCHESTRATOR_MODEL`, `OW_WORKER_MODEL`, `OW_SYNTHESIS_MODEL`

Example:

```bash
OW_FAST_MODE=1 OW_WORKER_MODEL=qwen3:0.6b python tutorials/module-2-workflow-patterns/10_orchestrator_worker.py
```

## Evaluator-Reflection Demo Controls (`11_evaluator_reflection.py`)

- input is interactive (press Enter to use default task)
- default writer model: `qwen3:0.6b`
- default critique model: `qwen2.5:0.5b` (different model to reduce same-model bias)
- optional env vars:
  - `ER_MODEL` (writer/draft-revise model)
  - `ER_CRITIQUE_MODEL` (critique model)
  - `ER_MIN_REVISIONS` and `ER_MAX_REVISIONS` (loop behavior)
  - `ER_FAST_MODE` (`0` default for more reliable structured retries)

Example:

```bash
ER_MIN_REVISIONS=2 ER_MAX_REVISIONS=5 ER_MODEL=qwen3:0.6b ER_CRITIQUE_MODEL=qwen2.5:0.5b python tutorials/module-2-workflow-patterns/11_evaluator_reflection.py
```

## Tool Calling Bridge (`12_tool_calling.py`)

- place this last to bridge from workflow patterns to full agents
- shows the app-controlled tool loop:
  - model requests tool
  - app executes tool
  - model finalizes answer using tool result
- uses `ask_ollama_structured(...)` from `workflow_utils.py`

Example:

```bash
python tutorials/module-2-workflow-patterns/12_tool_calling.py
```

## MCP Tool Discovery (`13_mcp_list_tools.py`)

- verifies MCP connectivity and auth
- prints available tool names/descriptions from Zapier MCP
- useful first check before direct tool invocation

Example:

```bash
python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py
```

## Direct MCP Notion Page Creation (`14_mcp_direct_tool_call.py`)

- prompts for page title
- inspects MCP schemas to determine parameter keys dynamically
- preflight-checks parent-page access in Notion
- creates page and prints page URL when available

Example:

```bash
python tutorials/module-2-workflow-patterns/14_mcp_direct_tool_call.py
```

## Qwen + MCP Notion Writer (`15_mcp_qwen_notion_writer.py`)

- prompts for topic/mode/page title
- generates structured content with Qwen (`doc` or `tasks`)
- renders markdown, creates Notion page, and appends content through MCP
- prints final page link

Example:

```bash
python tutorials/module-2-workflow-patterns/15_mcp_qwen_notion_writer.py
```

## Classroom Demo Prompts With Context

Use this section during live teaching to quickly demonstrate each pattern.

## `08_prompt_chaining.py` (meeting-notes text file input)

Context: show how raw notes become structured minutes, then an action plan.

Sample notes text A:

```text
Sprint planning: Team agreed to ship login redesign by May 5. Priya owns frontend, Arun owns API. Open question: should MFA be mandatory at launch? Risk: QA bandwidth is limited next week.
```

Sample notes text B:

```text
Faculty meeting notes: finalize AI lab rubric by Friday, create 3 student groups per section, reserve lab 204 for Thursday demos, pending decision on late-submission policy.
```

Tip: run with explicit file path from repo root:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
```

## `09_routing.py` (single user message)

Context: classify input and route to the right handler.

Sample prompt A:

```text
Checkout freezes when I apply a coupon code after the latest release.
```

Sample prompt B:

```text
Please add bulk export to CSV for invoices.
```

Sample prompt C:

```text
The onboarding flow was smooth and support was excellent.
```

## `10_orchestrator_worker.py` (planning task)

Context: one orchestrator breaks work into specialized worker tasks, then synthesizes.

Sample prompt A:

```text
Create a 2-week study plan for a student balancing exams and a 20-hour part-time job.
```

Sample prompt B:

```text
Design a project execution plan for launching a campus AI workshop in 10 days.
```

## `11_evaluator_reflection.py` (executive update task)

Context: generate draft, critique quality, revise in a loop.

Sample prompt A:

```text
Write a short executive update on the status of our Generative AI class project, including progress, blockers, and next steps.
```

Sample prompt B:

```text
Draft an executive update for leadership on pilot deployment outcomes and required decisions this week.
```

## `12_tool_calling.py` (tool-use query)

Context: model decides whether a tool is needed; app executes tool and returns final answer.

Sample prompt A:

```text
Read the local course note and tell me the two most important reminders.
```

Sample prompt B:

```text
Open the sample note and extract all deadlines and setup tasks.
```

## `13_mcp_list_tools.py` (no prompt required)

Context: verify MCP connectivity and inspect available tools before invoking any.

Instructor framing line:

```text
Let's verify MCP connectivity and inspect which tools are available before calling anything.
```

## `14_mcp_direct_tool_call.py` (Notion page title)

Context: direct MCP tool invocation to create a page.

Sample page title A:

```text
GenAI Class Demo Notes - Week 2
```

Sample page title B:

```text
Capstone Planning - Action Items
```

## `15_mcp_qwen_notion_writer.py` (topic, mode, title)

Context: LLM generates structured content, then MCP writes it to Notion.

Sample input set A:

```text
Topic: How MCP enables practical classroom agents
Mode: doc
Page title: MCP Classroom Brief
```

Sample input set B:

```text
Topic: Tasks to prepare for AI lab demo day
Mode: tasks
Page title: AI Lab Demo Checklist
```

## Expected Student Observations

- Tool calls are requested by the model but executed by Python
- Prompt chaining creates inspectable intermediate artifacts
- Routing sends inputs to different handlers/models based on classification
- Orchestrator-worker shows one planner coordinating multiple specialized workers
- Evaluator-reflection shows explicit quality control through critique-revise loops
- Tool-calling serves as a bridge from workflow patterns to agent loops
- MCP discovery clarifies what remote tools are actually available
- Schema-driven tool argument mapping improves connector resilience
- LLM generation + MCP execution creates a practical end-to-end agent workflow
