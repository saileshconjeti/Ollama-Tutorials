# Workflow Patterns

Date: **April 24, 2026**

## Learning Materials

- Theory: [LEARN.md](tutorials/april-24-workflow-patterns/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/april-24-workflow-patterns/BUILD.md)

## Planned Coverage

- `07_tool_calling.py`: Model requests tools, application executes tools
- `08_prompt_chaining.py`: Multi-step prompt chain with structured intermediate state
- `09_routing.py`: Classification-based routing to specialized handlers/LLMs

## Run Order (Next Class)

From repo root:

```bash
python tutorials/april-24-workflow-patterns/07_tool_calling.py
python tutorials/april-24-workflow-patterns/08_prompt_chaining.py
python tutorials/april-24-workflow-patterns/09_routing.py
```

## Prompt Chaining Arguments (`08_prompt_chaining.py`)

Optional CLI arguments:

- `--file`: path to input meeting-notes text file
- `--output`: path for generated markdown report

Examples:

```bash
python tutorials/april-24-workflow-patterns/08_prompt_chaining.py
python tutorials/april-24-workflow-patterns/08_prompt_chaining.py --file tutorials/april-24-workflow-patterns/sample_meeting_minutes.txt --output tutorials/april-24-workflow-patterns/my_minutes_report.md
```

## Learning Focus

- Separate model reasoning steps into explicit workflow stages
- Add deterministic control via application code
- Route requests based on classification and inspect graph state
