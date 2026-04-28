# BUILD - AI Agents

Module: **Module 3**

## Build Objective

Run and explain four agent patterns in sequence:

1. ReAct loop
2. Memory-backed personalization
3. Planner -> specialist executor graph
4. Supervisor-coordinated multi-agent graph

Each script is intentionally verbose in logging and comments so students can trace internal decisions.

## Prerequisites

- `ollama serve` is running
- Python virtual environment is active
- dependencies installed from repo root: `python -m pip install -r requirements.txt`
- for Groq variants (`*_groq.py`), `GROQ_API_KEY` is set in `.env`
- model available:
  - `qwen2.5:0.5b` (or set `OLLAMA_CHAT_MODEL` to your preferred local model)

## Create Your `.env` File (Do Not Commit)

Create a `.env` file at the repository root and add:

```dotenv
OLLAMA_CHAT_MODEL=qwen2.5:0.5b
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
# Optional:
# LLM_PROVIDER=groq
```

Notes:
- Keep real keys only in local `.env`; do not commit this file.
- `.gitignore` excludes `.env` and `.env.*` so secrets are not pushed.

## Environment Setup

Run once from repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For every new terminal:

```bash
source .venv/bin/activate
```

## Run Order

Run from repository root:

```bash
python tutorials/module-3-ai-agents/16_react_agent_loop.py
python tutorials/module-3-ai-agents/17_memory_agent.py
python tutorials/module-3-ai-agents/18_planner_executor_agent.py
python tutorials/module-3-ai-agents/19_multi_agent_supervisor.py
```

## Groq Variant Execution (`*_groq.py`)

Use these to run Module 3 agents with provider selection (`--provider ollama|groq`):

```bash
python tutorials/module-3-ai-agents/16_react_agent_loop_groq.py --provider groq
python tutorials/module-3-ai-agents/17_memory_agent_groq.py --provider groq
python tutorials/module-3-ai-agents/18_planner_executor_agent_groq.py --provider groq
python tutorials/module-3-ai-agents/19_multi_agent_supervisor_groq.py --provider groq
```

Recommended lecture pacing: `16 -> 17 -> 18 -> 19`.  
Reason: this order moves from single-loop autonomy to memory, then to graph orchestration.

## 16 - ReAct Agent Loop (`16_react_agent_loop.py`)

### What this build demonstrates

- structured decision per iteration (`AgentStep`)
- explicit tool dispatch in Python (`run_tool`)
- feedback cycle using trajectory as short-term memory
- guardrails:
  - bounded loop via `MAX_STEPS`
  - "must use tool evidence" before `finish`

### What students should observe in output

- `THOUGHT` and `ACTION` per step
- tool observations returning to the next prompt
- stop condition when action becomes `finish`
- Python `for/else` behavior when max steps are hit without break

### Suggested prompts

```text
Find all reminders related to exam preparation and attendance. Then calculate 72+19 and 205+37. End with a prioritized checklist.
```

```text
Extract deadline and office-hour reminders from notes, compute 44+58, and give a 5-day revision plan.
```

## 17 - Memory Agent (`17_memory_agent.py`)

### What this build demonstrates

- two-stage memory pipeline:
  - extract memory deltas (`detect_memory_updates`)
  - generate personalized reply (`build_reply`)
- persistent memory file: `tutorials/module-3-ai-agents/data/agent_memory.json`
- deduplication and growth control via `merge_unique(..., limit=10)`

### What students should observe in output

- `MEMORY BEFORE`, `MEMORY UPDATE`, `MEMORY AFTER`
- continuity across script reruns
- explainability via `used_memory_items`

### Suggested multi-run flow

1. Seed identity and preferences.
2. Ask for a lesson plan and check personalization.
3. Add new facts and rerun.
4. Confirm memory is cumulative, deduplicated, and capped.

Example seed:

```text
Hi, I am Priya. I prefer concise answers with bullet points and practical examples.
```

## 18 - Planner Executor Graph (`18_planner_executor_agent.py`)

### What this build demonstrates

- planner generates ordered role-based steps (`Plan`)
- dispatcher loads active step fields (`active_step_*`)
- conditional routing by role (`route_from_dispatch`)
- specialist loop executes until `step_index` reaches plan length
- reviewer synthesizes full execution into `final_report`

### What students should observe in output

- planner JSON appears first
- per-step specialist output appears in sequence
- state cursor (`step_index`) advances after each specialist run
- graph exits only after reviewer node completes

### Suggested prompts

```text
Create a 2-week beginner-friendly project where students build a study-planner chatbot with memory.
```

```text
Build a multi-agent solution for triaging university IT helpdesk tickets.
```

## 19 - Multi-Agent Supervisor (`19_multi_agent_supervisor.py`)

### What this build demonstrates

- delegation planning for fixed roles (`researcher`, `architect`, `reviewer`)
- parallel worker branches from one planner node
- merged branch outputs using:
  - `worker_outputs: Annotated[list[dict], operator.add]`
- supervisor synthesis into one final strategy report

### What students should observe in output

- one delegation plan
- multiple worker outputs (merge order may vary)
- one consolidated supervisor report

### Suggested prompts

```text
Design an internal HR assistant project with privacy constraints and clear escalation rules.
```

```text
Create a capstone project for healthcare students to summarize clinical notes with safety checks.
```

## Troubleshooting

- If Ollama is not running, model calls fail immediately.
- If responses are weak, switch model with `OLLAMA_CHAT_MODEL`.
- If memory behavior seems stale, inspect:
  - `tutorials/module-3-ai-agents/data/agent_memory.json`
- If graph output seems confusing, compare printed sections in order:
  - planner -> workers/specialists -> reviewer/supervisor

## Teaching Notes

- Contrast with Module 2:
  - Module 2: deterministic workflow control
  - Module 3: autonomous loops, memory, delegation, synthesis
- Ask students to map each printed section to code nodes/functions.
- Emphasize safety controls:
  - schema-constrained outputs
  - explicit Python tool execution
  - bounded loops
  - typed shared state
