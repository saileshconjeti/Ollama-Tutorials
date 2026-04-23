# AI Agents

Module: **Module 3**

## Learning Materials

- Theory: [LEARN.md](tutorials/module-3-ai-agents/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/module-3-ai-agents/BUILD.md)

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

- `16_react_agent_loop.py`: ReAct-style think-act-observe loop with explicit tools
- `17_memory_agent.py`: Personalized memory agent with persistent user preferences
- `18_planner_executor_agent.py`: Planner-executor agent with iterative LangGraph execution
- `19_multi_agent_supervisor.py`: Supervisor delegates to specialized agents and synthesizes output
- `agent_utils.py`: Shared helper utilities for structured output and terminal display

## Run Order

From repo root:

```bash
python tutorials/module-3-ai-agents/16_react_agent_loop.py
python tutorials/module-3-ai-agents/17_memory_agent.py
python tutorials/module-3-ai-agents/18_planner_executor_agent.py
python tutorials/module-3-ai-agents/19_multi_agent_supervisor.py
```

## Learning Focus

- Understand how an agent loops over reasoning and actions
- Separate short-term execution from long-term user memory
- Implement planning and stepwise execution with graph state
- Coordinate multiple specialized agents under a supervisor
- Compare workflow patterns (Module 2) vs autonomous agent patterns (Module 3)
