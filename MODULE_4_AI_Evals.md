# AI Evals - LLM-as-a-Judge

Module: **Module 4**

## Learning Materials

- Theory: [LEARN.md](tutorials/module_4_ai_evals/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/module_4_ai_evals/BUILD.md)

## Setup

Run once at the beginning of class from repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Module 4 also includes a minimal standalone requirements file:

```bash
cd tutorials/module_4_ai_evals
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your Groq API key to `tutorials/module_4_ai_evals/.env`:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

## Module Topics

- `01_llm_as_judge_qa.py`: Reference-based Q&A evaluation with accuracy, relevance, and completeness scores
- `02_pairwise_llm_judge.py`: Pairwise comparison of two candidate responses
- `03_bias_mitigation_position_swapping.py`: Position-bias test using answer order swapping
- `04_multiple_llm_judges.py`: Cross-model judging with multiple Groq-hosted LLMs and score aggregation
- `utils/groq_client.py`: Groq chat completion helper with `.env` loading
- `utils/prompts.py`: Reusable judge prompts and rubrics
- `utils/json_utils.py`: Robust JSON extraction from LLM judge output

## Run Order

From the Module 4 folder:

```bash
cd tutorials/module_4_ai_evals
python 01_llm_as_judge_qa.py
python 02_pairwise_llm_judge.py
python 03_bias_mitigation_position_swapping.py
python 04_multiple_llm_judges.py
```

## Groq Judge Models

The default judge model is configured with:

```dotenv
GROQ_MODEL=llama-3.1-8b-instant
```

The multi-judge tutorial uses:

- `llama-3.1-8b-instant`
- `openai/gpt-oss-20b`
- `qwen/qwen3-32b`

If a model is unavailable for your Groq account, replace it with another supported Groq chat model.

## Learning Focus

- Understand why LLM application outputs need evaluation beyond exact string matching
- Use LLM-as-a-Judge for reference-based answer grading
- Compare candidate answers with pairwise evaluation
- Detect position bias by swapping answer order
- Reduce single-model judge bias with multiple judge LLMs
- Use rubrics and structured JSON outputs for inspectable evaluation results
- Connect automated judge scores with human review and golden datasets
