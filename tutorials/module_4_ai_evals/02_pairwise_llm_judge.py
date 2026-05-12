# File name: 02_pairwise_llm_judge.py
# Purpose: Compare two candidate responses using LLM-as-a-Judge.
# How to run: python 02_pairwise_llm_judge.py

import json

from utils.groq_client import call_groq_llm, get_selected_groq_model
from utils.json_utils import extract_json
from utils.prompts import PAIRWISE_EVALUATION_PROMPT


# Pairwise evaluation compares two answers to the same question.
question = "Explain the difference between zero-shot and few-shot prompting."

# Response A is intentionally correct and concise.
response_a = """
Zero-shot prompting means asking a model to perform a task without giving examples. Few-shot prompting means including a small number of examples in the prompt so the model can infer the expected pattern.
"""

# Response B is intentionally flawed: it confuses prompting with model training.
response_b = """
Zero-shot prompting is when the model has no training data. Few-shot prompting is when the model is trained on a few examples. Both are training techniques used to update the model weights.
"""


def main():
    print("\n=== Module 4 - AI Evals: LLM-as-a-Judge ===")
    print(f"Provider: groq | Model: {get_selected_groq_model()}")

    # Build a pairwise prompt that asks the judge to compare A and B.
    prompt = PAIRWISE_EVALUATION_PROMPT.format(
        question=question,
        response_a=response_a,
        response_b=response_b,
    )

    # A low temperature makes the judging behavior more repeatable for demos.
    raw_result = call_groq_llm(prompt, temperature=0.0)

    # The prompt asks for JSON, but extract_json also handles extra text if the
    # model adds a short explanation outside the JSON object.
    result = extract_json(raw_result)

    print("\n=== 02 - Pairwise LLM-as-a-Judge Evaluation ===")
    print("\nQuestion:")
    print(question)
    print("\nResponse A:")
    print(response_a.strip())
    print("\nResponse B:")
    print(response_b.strip())
    print("\nJudge result:")
    print(json.dumps(result, indent=2))
    print("\nTeaching point:")
    print(
        "Response A should usually win because it correctly describes prompting. "
        "Response B confuses prompting with training or fine-tuning."
    )


if __name__ == "__main__":
    main()
