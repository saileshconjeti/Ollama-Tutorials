# BUILD - Workflow Patterns

Module: **Module 2**

## Prerequisites

- `ollama serve` is running
- Python virtual environment is active
- dependencies installed from repo root: `python -m pip install -r requirements.txt`
- for Groq variants (`*_groq.py`), `GROQ_API_KEY` is set in `.env`
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
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
# Optional (11_evaluator_reflection_groq.py only):
# ER_GROQ_CRITIQUE_MODEL=llama-3.3-70b-versatile
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
python tutorials/module-2-workflow-patterns/15_mcp_groq_notion_writer.py
```

## Groq Variant Execution (`*_groq.py`)

Use these to run Module 2 workflows with provider selection (`--provider ollama|groq`):

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider groq
python tutorials/module-2-workflow-patterns/09_routing_groq.py --provider groq
python tutorials/module-2-workflow-patterns/10_orchestrator_worker_groq.py --provider groq
python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider groq
python tutorials/module-2-workflow-patterns/12_tool_calling_groq.py --provider groq
python tutorials/module-2-workflow-patterns/15_mcp_groq_notion_writer.py
```

## Prompt Chaining CLI Arguments (`08_prompt_chaining.py`)

- `--file`: input `.txt` minutes file
- `--output`: output `.md` report path

Examples:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
```

Groq variant examples:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider groq
python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider groq --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
```

## Suggested Routing Demo Inputs (`09_routing.py`)

- Bug report: "Checkout freezes when I apply a coupon."
- Feature request: "Please add bulk invoice export."
- Praise/general feedback: "Onboarding was smooth and support was excellent."

Groq variant run:

```bash
python tutorials/module-2-workflow-patterns/09_routing_groq.py --provider groq
```

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

Groq variant run:

```bash
python tutorials/module-2-workflow-patterns/10_orchestrator_worker_groq.py --provider groq
```

### Suggested Prompt Inputs (`10_orchestrator_worker.py` and `10_orchestrator_worker_groq.py`)

- `Create a 2-week exam prep plan for a student taking Data Structures and DBMS while working a part-time job 15 hours/week. Student is weak in recursion and SQL joins, has classes Mon-Fri 9am-2pm, and can study 2 hours on weekdays and 5 hours on weekends.`
- `Design a 14-day recovery plan for a student who has only 2 weeks left before finals in Operating Systems and Computer Networks. Constraints: student gets tired after 10pm, has anxiety before tests, and loses focus after 45 minutes. Include realistic breaks and fallback options for low-energy days.`
- `Build a practical study plan for a student preparing for 3 subjects: Machine Learning, Probability, and Linear Algebra. Total available time is 25 hours/week for 2 weeks. Student has strong ML basics but weak math foundations. Prioritize high-yield topics and include revision checkpoints.`
- `Create a 2-week preparation strategy for campus placement aptitude + coding interviews. Student can spend 3 hours/day weekdays and 6 hours/day weekends. Needs practice in arrays, strings, and mock interviews. Include daily structure, practice targets, and burnout prevention.`

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

Groq variant run:

```bash
python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider groq
```

Optional Groq critique override:

```bash
ER_GROQ_CRITIQUE_MODEL=llama-3.3-70b-versatile python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider groq
```

### Suggested Prompt Inputs (`11_evaluator_reflection.py` and `11_evaluator_reflection_groq.py`)

- `Write a short executive update on our Generative AI class project, covering progress, blockers, and next actions for this week.`
- `Draft an executive update for leadership on pilot deployment outcomes, including measurable impact, key risks, and decisions needed by Friday.`
- `Create an executive update for a university AI lab rollout that is behind schedule; include what slipped, why it slipped, and a realistic recovery plan.`
- `Write an executive update about a customer-support chatbot launch: summarize current quality metrics, unresolved issues, and immediate mitigation steps.`

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

Groq variant run:

```bash
python tutorials/module-2-workflow-patterns/12_tool_calling_groq.py --provider groq
```

### Suggested Prompt Inputs (`12_tool_calling.py` and `12_tool_calling_groq.py`)

- `Read the local course note and tell me the two most important reminders.`
- `Multiply 17.5 by 8 and explain the result in one sentence.`
- `What day of the week is 2026-05-15?`
- `Check whether the word "Ollama" appears in this text: "Install Ollama before class and test one model."`
- `Estimate study time for 9 topics at 35 minutes per topic.`
- `Count words in this text: "RAG retrieves context before generation to improve grounding."`
- `Add 145.2 and 89.8, then round to the nearest whole number.`
- `Just explain in plain words why tool calling is useful in agent workflows.`

## MCP Tool Discovery (`13_mcp_list_tools.py`)

- verifies MCP connectivity and auth
- prints available tool names/descriptions from Zapier MCP
- useful first check before direct tool invocation

Example:

```bash
python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py
```

### Zapier MCP Tool Modes (Important)

Current Zapier MCP deployments may expose either:

- Legacy per-app tools (for example `notion_create_page`, `notion_retrieve_a_page`)
- Generic execution tools (`execute_zapier_read_action`, `execute_zapier_write_action`) with action keys discovered through `list_enabled_zapier_actions`

The Module 2 Notion scripts now detect and adapt to both modes at runtime.

## Direct MCP Notion Page Creation (`14_mcp_direct_tool_call.py`)

- prompts for page title
- inspects MCP schemas to determine parameter keys dynamically
- preflight-checks parent-page access in Notion
- creates page and prints page URL when available
- supports both legacy and generic Zapier MCP tool modes

Example:

```bash
python tutorials/module-2-workflow-patterns/14_mcp_direct_tool_call.py
```

## MCP Notion Writer Variants (`15_mcp_qwen_notion_writer.py`, `15_mcp_groq_notion_writer.py`)

- prompts for topic/mode/page title
- generates structured content (`doc` or `tasks`) and renders markdown
- creates Notion page and appends content through MCP
- handles follow-up create prompts from Zapier MCP by retrying with explicit defaults
- prints final page link

Example:

```bash
python tutorials/module-2-workflow-patterns/15_mcp_qwen_notion_writer.py
python tutorials/module-2-workflow-patterns/15_mcp_groq_notion_writer.py
```

## Troubleshooting (MCP + Notion)

### `Tool 'notion_create_page' not found on the MCP server`

Cause:
- Your Zapier MCP server is exposing generic execute tools instead of legacy per-app Notion tool names.

Fix:
1. Run `python tutorials/module-2-workflow-patterns/13_mcp_list_tools.py`.
2. Confirm you see `execute_zapier_read_action` and `execute_zapier_write_action`.
3. Use the updated scripts in this module; they auto-detect legacy vs generic tool mode.

### `followUpQuestion` returned when creating a Notion page

Cause:
- Zapier sometimes asks a clarification question (content/icon/cover) instead of executing immediately.

Fix:
1. Use the updated writer scripts; they auto-retry create with explicit defaults.
2. If testing manually, re-run create with clear instructions to proceed with title + parent only.

### `The page appears to have been created, but no page ID was extracted from the result`

Cause:
- The create call returned a follow-up prompt or a payload shape without immediate `page_id`.

Fix:
1. Check the raw tool result printed above the error.
2. If it contains `followUpQuestion`, re-run with explicit "proceed now" instructions.
3. Ensure you are on the latest module scripts that handle this automatically.

### Parent page access / visibility errors

Cause:
- The configured `NOTION_PARENT_PAGE_ID` is not shared with the same Notion integration used by Zapier.

Fix:
1. In Notion, open the parent page.
2. Click `Share` and invite the Zapier integration/account used in MCP.
3. Re-run preflight (`14_mcp_direct_tool_call.py` or `15_mcp_*_notion_writer.py`).

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

Sample prompt C:

```text
Create a 2-week exam prep plan for a student taking Data Structures and DBMS while working a part-time job 15 hours/week. Student is weak in recursion and SQL joins, has classes Mon-Fri 9am-2pm, and can study 2 hours on weekdays and 5 hours on weekends.
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

Sample prompt C:

```text
Create an executive update for a university AI lab rollout that is behind schedule; include what slipped, why it slipped, and a realistic recovery plan.
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

## `15_mcp_qwen_notion_writer.py` / `15_mcp_groq_notion_writer.py` (topic, mode, title)

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
