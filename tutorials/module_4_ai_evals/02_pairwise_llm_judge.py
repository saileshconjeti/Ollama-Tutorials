# File name: 02_pairwise_llm_judge.py
# Purpose: Compare two candidate responses using LLM-as-a-Judge.
# How to run: python 02_pairwise_llm_judge.py

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.groq_client import call_groq_llm, get_selected_groq_model
from utils.json_utils import extract_json
from utils.prompts import PAIRWISE_EVALUATION_PROMPT
from tutorials.terminal_utils import print_ascii_tree, print_header, print_json, print_kv, print_prompt_preview, print_step


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
    print_header("Pairwise LLM-as-a-Judge Evaluation")
    print("What this demonstrates: a judge compares two candidate answers and chooses the better one.")

    print_step(1, "Checking provider and model")
    print_kv("Evaluation type", "pairwise")
    print_kv("Provider", "groq")
    print_kv("Judge model", get_selected_groq_model())

    print_step(2, "Inspecting pairwise data flow")
    print_ascii_tree(
        """
        User Question
            |
            v
        Response A ----+
                       |
                       v
        Response B -> Pairwise Judge Prompt -> Groq Model -> Winner + Scores
        """
    )

    print_step(3, "Reviewing inputs and rubric")
    print_kv("User question", question)
    print("\nResponse A:")
    print(response_a.strip())
    print("\nResponse B:")
    print(response_b.strip())
    print("\nRubric: accuracy, relevance, completeness, and clarity.")

    # Build a pairwise prompt that asks the judge to compare A and B.
    prompt = PAIRWISE_EVALUATION_PROMPT.format(
        question=question,
        response_a=response_a,
        response_b=response_b,
    )
    print_step(4, "Preparing judge prompt")
    print_prompt_preview(prompt, max_chars=900)

    # A low temperature makes the judging behavior more repeatable for demos.
    print_step(5, "Sending request to Groq")
    raw_result = call_groq_llm(prompt, temperature=0.0)
    print("Raw judge response:")
    print(raw_result)

    # The prompt asks for JSON, but extract_json also handles extra text if the
    # model adds a short explanation outside the JSON object.
    print_step(6, "Parsing JSON response")
    result = extract_json(raw_result)
    print_json(result)

    print_step(7, "Final interpretation")
    print(f"Winner: {result.get('winner', '[missing]')}")
    print(f"Score A: {result.get('score_a', '[missing]')}/5")
    print(f"Score B: {result.get('score_b', '[missing]')}/5")
    print(f"Reasoning: {result.get('reasoning', '[missing]')}")
    print()
    print(
        "Response A should usually win because it correctly describes prompting. "
        "Response B confuses prompting with training or fine-tuning."
    )


if __name__ == "__main__":
    main()
