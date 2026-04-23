# LEARN - AI Agents

Module: **Module 3**

## Learning Outcomes

By the end of this module, students should be able to:

- distinguish deterministic workflows from autonomous agent loops
- trace a ReAct cycle using structured state: thought, action, observation
- explain why tool execution should remain in application code
- distinguish short-term trajectory memory from persistent user memory
- describe when planner-executor beats single-agent prompting
- explain how supervisor-driven multi-agent delegation improves coverage
- inspect typed graph state and reason about transitions node by node

## Core Mental Model

Think of Module 3 as increasing capability in four stages:

1. `16_react_agent_loop.py`: one agent iterates with tools
2. `17_memory_agent.py`: one agent remembers across runs
3. `18_planner_executor_agent.py`: one planner coordinates specialist steps
4. `19_multi_agent_supervisor.py`: one supervisor coordinates parallel workers

The progression is intentional:

- first learn local control in a loop
- then add persistence
- then add role-based orchestration
- then add parallel delegation and synthesis

## Concept Breakdown

## 1) ReAct Agent Loop (`16_react_agent_loop.py`)

What to learn:

- agent decisions are schema-constrained via `AgentStep`
- each iteration follows: decide -> act -> observe -> append trajectory
- trajectory is short-term working memory for the next decision
- loop termination is explicit (`finish`) and bounded (`MAX_STEPS`)

Why this pattern matters:

- makes reasoning inspectable
- avoids hidden tool execution inside model output
- introduces guardrails before larger autonomous systems

## 2) Memory Agent (`17_memory_agent.py`)

What to learn:

- memory extraction and reply generation are separated
- memory is persisted in JSON to survive process restarts
- updates are merged with deduplication and size limits
- reply includes `used_memory_items` for explainability

Why this pattern matters:

- personalization without retraining
- transparent and editable memory state
- controllable context growth

## 3) Planner-Executor Graph (`18_planner_executor_agent.py`)

What to learn:

- planner creates ordered steps and success criteria
- dispatcher maps current step into `active_step_*` state keys
- router sends control to specialist role nodes
- specialists append outputs and advance `step_index`
- reviewer synthesizes all outputs into final report

Why this pattern matters:

- decomposes complex goals into manageable sub-problems
- role prompts improve output quality and consistency
- graph state gives reliable progress tracking

## 4) Multi-Agent Supervisor (`19_multi_agent_supervisor.py`)

What to learn:

- supervisor creates role assignments first
- workers execute in parallel branches
- shared outputs merge using `Annotated[..., operator.add]`
- supervisor composes one strategic answer from all workers

Why this pattern matters:

- specialization improves solution breadth
- parallelism improves throughput for independent subtasks
- synthesis stage resolves conflicting perspectives

## State and Safety Principles Across Module 3

- typed schemas reduce ambiguous model outputs
- explicit Python tool calls improve determinism and safety
- bounded loops prevent runaway agent behavior
- persisted memory is auditable and resettable
- graph state makes control flow debuggable in class

## Suggested Classroom Discussion Questions

1. What failure modes appear if `MAX_STEPS` is removed from ReAct?
2. What should and should not be stored in persistent memory?
3. When should we choose planner-executor over one strong prompt?
4. Which tasks benefit from parallel multi-agent workers?
5. How can we test whether a final answer is truly grounded in tool or worker evidence?

## Files Covered

- `16_react_agent_loop.py`
- `17_memory_agent.py`
- `18_planner_executor_agent.py`
- `19_multi_agent_supervisor.py`
- `agent_utils.py`
- `data/agent_memory.json` (generated at runtime)
