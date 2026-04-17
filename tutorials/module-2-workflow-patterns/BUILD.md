# BUILD - Workflow Patterns

Module: **Module 2**

## Prerequisites

- `ollama serve` is running
- Python virtual environment is active
- dependencies installed: `pip install -r requirements.txt`
- models available:
  - `qwen3:4b`
  - `qwen3-embedding:0.6b`

## Step-by-Step Execution

Run from repository root.

```bash
python tutorials/module-2-workflow-patterns/07_tool_calling.py
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/09_routing.py
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

## Expected Student Observations

- Tool calls are requested by the model but executed by Python
- Prompt chaining creates inspectable intermediate artifacts
- Routing sends inputs to different handlers/models based on classification
