# BUILD - AI Evals: LLM-as-a-Judge

Module: **Module 4**

## Build Objective

Run and explain four AI evaluation patterns in sequence:

1. Reference-based LLM-as-a-Judge evaluation
2. Pairwise LLM judging
3. Position-bias testing with answer swapping
4. Multiple LLM judges with score aggregation

Each script is intentionally small and verbose so students can trace how the prompt, model call, JSON parsing, and printed interpretation fit together.

Terminal output now shows evaluation type, provider/model, user question, candidate/reference answers, rubric, judge prompt preview, raw judge response, parsed JSON, and a plain-English interpretation. Setup and JSON parsing errors include actionable classroom debugging steps.

## Prerequisites

- Python virtual environment is active
- dependencies installed from repo root: `python -m pip install -r requirements.txt`
- for module-local setup, dependencies installed from this folder: `python -m pip install -r requirements.txt`
- `GROQ_API_KEY` is set in `.env`
- default Groq model available:
  - `llama-3.1-8b-instant`
- tutorial `04_multiple_llm_judges.py` also calls:
  - `openai/gpt-oss-20b`
  - `qwen/qwen3-32b`

## Create Your `.env` File (Do Not Commit)

Create a `.env` file in `tutorials/module_4_ai_evals` and add:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

You can also copy the template:

```bash
cd tutorials/module_4_ai_evals
cp .env.example .env
```

Notes:
- Keep real keys only in local `.env`; do not commit this file.
- The default model is configurable through `GROQ_MODEL`.
- If one of the models in `04_multiple_llm_judges.py` is unavailable for your Groq account, replace it with another Groq chat model available to you.

## Environment Setup

Option A: use the shared course environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Option B: use a module-local environment:

```bash
cd tutorials/module_4_ai_evals
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell:

```powershell
cd tutorials/module_4_ai_evals
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Run Order

Run from `tutorials/module_4_ai_evals`:

```bash
python 01_llm_as_judge_qa.py
python 02_pairwise_llm_judge.py
python 03_bias_mitigation_position_swapping.py
python 04_multiple_llm_judges.py
```

## 01 - Reference-Based Q&A Evaluation (`01_llm_as_judge_qa.py`)

### What this build demonstrates

- create a user question, assistant response, and reference answer
- fill a rubric-based evaluation prompt
- call a Groq-hosted LLM as the judge
- parse JSON with `extract_json(...)`
- print the original inputs and structured judge result

### What students should observe in output

- scores for accuracy, relevance, and completeness
- short reasoning from the judge
- a teaching note explaining reference-based evaluation

### Teaching point

Reference-based evaluation compares an answer to a known ground truth. This is useful for golden datasets, but the judge still needs a rubric because correct natural language answers can use different wording.

## 02 - Pairwise LLM Judge (`02_pairwise_llm_judge.py`)

### What this build demonstrates

- compare two responses to the same user question
- evaluate with a rubric covering accuracy, relevance, completeness, and clarity
- return `A`, `B`, or `tie`
- print scores and reasoning for both responses

### What students should observe in output

- response A should usually win
- response B confuses prompting with training or fine-tuning
- pairwise comparison is easier than absolute scoring in some cases

### Teaching point

Pairwise evaluation is useful when comparing prompts, models, retrieval settings, or agent designs. It asks which output is better, not whether one output exactly matches a reference.

## 03 - Position Bias and Answer Swapping (`03_bias_mitigation_position_swapping.py`)

### What this build demonstrates

- run the same pairwise comparison twice
- first run: stronger answer as A, weaker answer as B
- second run: weaker answer as A, stronger answer as B
- map the winner back to stable candidate names
- print whether the result is stable across answer order

### What students should observe in output

- `candidate_1` should usually win in both orders
- if the winner changes, the judge may be sensitive to answer position
- stable winners are easier to trust than order-dependent winners

### Teaching point

LLM judges can have position bias. Swapping answer order is a simple classroom-friendly mitigation that exposes whether the result depends on presentation order.

## 04 - Multiple LLM Judges (`04_multiple_llm_judges.py`)

### What this build demonstrates

- run the same reference-based evaluation through multiple judge models
- use three Groq-hosted models:
  - `llama-3.1-8b-instant`
  - `openai/gpt-oss-20b`
  - `qwen/qwen3-32b`
- average accuracy, relevance, and completeness scores
- compute a simple majority pass or needs-review decision

### What students should observe in output

- different judge models may score or explain the same response slightly differently
- aggregated scores are less dependent on one model's preferences
- model ensembles can improve robustness but do not remove the need for human review

### Teaching point

Cross-model evaluation reduces the chance that a single model's stylistic preferences dominate the result. It is especially useful when evaluating outputs from a model that may otherwise judge its own style too favorably.

## Utility Files

- `utils/groq_client.py`: loads `.env`, validates `GROQ_API_KEY`, and calls Groq chat completions
- `utils/prompts.py`: stores reusable judge prompts
- `utils/json_utils.py`: extracts JSON from model output, including outputs with extra prose

## Troubleshooting

- If you see a missing API key error, check that `.env` exists in `tutorials/module_4_ai_evals` and contains `GROQ_API_KEY`.
- If a model is unavailable, update `GROQ_MODEL` or the `JUDGE_MODELS` list in `04_multiple_llm_judges.py`.
- If JSON parsing fails, inspect the raw model output shown in the error. LLMs can occasionally add extra prose or malformed JSON even when instructed not to.
- If results vary slightly across runs, discuss this as part of the lesson: evaluator stability is itself something we need to measure.
