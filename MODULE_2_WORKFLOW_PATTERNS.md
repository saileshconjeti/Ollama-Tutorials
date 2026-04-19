# Workflow Patterns

Module: **Module 2**

## Learning Materials

- Theory: [LEARN.md](tutorials/module-2-workflow-patterns/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/module-2-workflow-patterns/BUILD.md)

## Module Topics

- `08_prompt_chaining.py`: Multi-step prompt chain with structured intermediate state
- `09_routing.py`: Classification-based routing to specialized handlers/LLMs
- `10_orchestrator_worker.py`: One orchestrator delegates to specialized workers and synthesizes outputs
- `11_evaluator_reflection.py`: Critique-revise loop with explicit quality control
- `12_tool_calling.py`: Tool-calling bridge from workflow patterns to agent loops

## Run Order

From repo root:

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining.py
python tutorials/module-2-workflow-patterns/09_routing.py
python tutorials/module-2-workflow-patterns/10_orchestrator_worker.py
python tutorials/module-2-workflow-patterns/11_evaluator_reflection.py
python tutorials/module-2-workflow-patterns/12_tool_calling.py
```

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
