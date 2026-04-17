# BUILD - Workflow Patterns

Module: **Module 2**

## Prerequisites

- `ollama serve` is running
- Python virtual environment is active
- dependencies installed: `pip install -r requirements.txt`
- models available:
  - `qwen3:0.6b`
  - `qwen2.5:0.5b`
  - `qwen3:4b` (optional, for higher-quality critique)
  - `qwen3-embedding:0.6b`

## Step-by-Step Execution

Run from repository root.

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/09_routing.py
python tutorials/module-2-workflow-patterns/11_orchestrator_worker.py
python tutorials/module-2-workflow-patterns/12_evaluator_reflection.py
python tutorials/module-2-workflow-patterns/13_tool_calling.py
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

## Orchestrator-Worker Demo Controls (`11_orchestrator_worker.py`)

- input is interactive (press Enter to use default topic)
- optional env vars:
  - `OW_FAST_MODE=1` (default) for faster runs
  - `OW_USE_LLM_ORCHESTRATOR=0` (default) for deterministic plan
  - `OW_ORCHESTRATOR_MODEL`, `OW_WORKER_MODEL`, `OW_SYNTHESIS_MODEL`

Example:

```bash
OW_FAST_MODE=1 OW_WORKER_MODEL=qwen3:0.6b python tutorials/module-2-workflow-patterns/11_orchestrator_worker.py
```

## Evaluator-Reflection Demo Controls (`12_evaluator_reflection.py`)

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
ER_MIN_REVISIONS=2 ER_MAX_REVISIONS=5 ER_MODEL=qwen3:0.6b ER_CRITIQUE_MODEL=qwen2.5:0.5b python tutorials/module-2-workflow-patterns/12_evaluator_reflection.py
```

## Tool Calling Bridge (`13_tool_calling.py`)

- place this last to bridge from workflow patterns to full agents
- shows the app-controlled tool loop:
  - model requests tool
  - app executes tool
  - model finalizes answer using tool result

Example:

```bash
python tutorials/module-2-workflow-patterns/13_tool_calling.py
```

## Expected Student Observations

- Tool calls are requested by the model but executed by Python
- Prompt chaining creates inspectable intermediate artifacts
- Routing sends inputs to different handlers/models based on classification
- Orchestrator-worker shows one planner coordinating multiple specialized workers
- Evaluator-reflection shows explicit quality control through critique-revise loops
- Tool-calling serves as a bridge from workflow patterns to agent loops
