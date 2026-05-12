# LEARN - AI Evals: LLM-as-a-Judge

Module: **Module 4**

## Theory Goals

By the end of this class, students should be able to:

- explain what AI evaluation means in LLM applications
- explain why exact-match evaluation is often insufficient for natural language outputs
- explain the LLM-as-a-Judge pattern
- distinguish reference-based evaluation from pairwise comparison
- evaluate a Q&A response against a reference answer
- compare two candidate model responses using a rubric
- explain why LLM judges can be biased
- test for position bias using answer swapping
- explain why rubrics, structured outputs, multiple judges, and human review matter

## Why AI Evals?

LLM apps are probabilistic. The same prompt can produce slightly different answers, and those answers can be correct, partially correct, irrelevant, verbose, incomplete, or hallucinated.

Traditional exact-match metrics are often insufficient for natural language outputs. If a student answer says "RAG retrieves relevant documents before generation" and a reference says "retrieval-augmented generation uses external sources as context," exact string matching would fail even though the meaning is similar.

Evals help us compare prompts, models, retrieval strategies, agent designs, and safety controls. They make development less dependent on intuition and more grounded in repeatable checks.

## What is LLM-as-a-Judge?

LLM-as-a-Judge is an evaluation pattern where an LLM is used as an evaluator. The judge receives the user question, a model response, and optionally a reference answer or another candidate response. It returns a structured judgment, such as scores and a short explanation.

This module covers two common modes:

1. Reference-based evaluation
- compare one model response against a known reference answer
- useful when a golden answer is available
- still requires careful rubric design because valid answers may differ in wording

2. Pairwise comparison
- compare two candidate responses to the same prompt
- useful when relative preference is easier than absolute scoring
- common for comparing prompts, model versions, retrieval strategies, or agent designs

## Concept Map

1. Reference-Based Q&A Evaluation (`01_llm_as_judge_qa.py`)
- evaluates one assistant response against a reference answer
- scores accuracy, relevance, and completeness
- returns structured JSON for downstream analysis
- demonstrates why semantic evaluation is more useful than exact string matching

2. Pairwise LLM Judge (`02_pairwise_llm_judge.py`)
- compares response A and response B for the same user question
- uses a rubric covering accuracy, relevance, completeness, and clarity
- returns a winner, scores, and short reasoning
- demonstrates that LLM-as-a-Judge can be used for relative model or prompt comparison

3. Position Bias Mitigation (`03_bias_mitigation_position_swapping.py`)
- runs pairwise evaluation twice with answer order swapped
- maps the winner back to stable candidate identities
- checks whether the same candidate wins in both positions
- demonstrates that judge outputs can be sensitive to presentation order

4. Multiple LLM Judges (`04_multiple_llm_judges.py`)
- runs the same reference-based evaluation through three Groq-hosted models
- averages rubric scores across judges
- reports a simple majority pass or needs-review decision
- demonstrates cross-model evaluation as one way to reduce single-model stylistic bias

## Bias and Reliability

LLM judges are useful, but they are not neutral measurement instruments. They can be affected by:

- position bias: preferring the first or second response
- verbosity bias: preferring longer answers even when concise answers are better
- self-preference bias: preferring outputs similar to the judge model's own style
- rubric ambiguity: making inconsistent judgments when criteria are vague
- model instability: producing different judgments across runs or models

Practical mitigation strategies include:

- Position swapping: run pairwise comparisons in both answer orders.
- Rubrics, not vibes: define explicit criteria such as accuracy, relevance, completeness, and clarity.
- Structured outputs: ask the judge to return JSON for easier analysis.
- Multiple judge LLMs: compare judgments from different models when possible.
- Human review: compare LLM-judge results with human expert ratings.
- Golden datasets: test the evaluator on examples where the expected judgment is known.

## Why This Matters

- Quality control: teams need repeatable ways to compare model outputs.
- Prompt iteration: evals reveal whether a prompt change improves or harms behavior.
- RAG development: evals help compare retrieval strategies and answer grounding.
- Agent safety: evals can test whether agents follow constraints and avoid unsafe behavior.
- Product reliability: structured evals help turn subjective impressions into inspectable evidence.
- Responsible deployment: LLM judges should support, not replace, human review in high-stakes settings.

## Classroom Discussion

Useful questions for students:

- What makes a rubric clear enough for an evaluator?
- When is reference-based evaluation better than pairwise evaluation?
- What kinds of model outputs are hard to evaluate automatically?
- How could a judge model be calibrated against human expert ratings?
- What risks appear if an LLM judge becomes the only evaluation method?
- How would you design a small golden dataset for your own LLM application?

## Files Covered

- `01_llm_as_judge_qa.py`
- `02_pairwise_llm_judge.py`
- `03_bias_mitigation_position_swapping.py`
- `04_multiple_llm_judges.py`
- `utils/groq_client.py`
- `utils/prompts.py`
- `utils/json_utils.py`
- `.env.example`
- `requirements.txt`
