# File name: 04_multiple_llm_judges.py
# Purpose: Run the same reference-based evaluation through multiple Groq models.
# How to run: python 04_multiple_llm_judges.py

import sys
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.groq_client import call_groq_llm
from utils.json_utils import extract_json
from utils.prompts import EVALUATION_PROMPT
from tutorials.terminal_utils import print_ascii_tree, print_header, print_json, print_kv, print_prompt_preview, print_step


# A small ensemble of Groq-hosted judge models.
# The goal is to avoid letting one model's preferences dominate the evaluation.
JUDGE_MODELS = [
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
]

# These fields must match the JSON keys requested in EVALUATION_PROMPT.
SCORE_FIELDS = ["accuracy", "relevance", "completeness"]

# A simple rule for the demo: a judge "passes" the response if its average
# rubric score is at least 4 out of 5.
PASS_THRESHOLD = 4.0

question = "What is retrieval-augmented generation, and why is it useful?"

assistant_response = """
Retrieval-augmented generation, or RAG, is a technique where an AI system retrieves relevant external documents before generating an answer. It is useful because it can make answers more grounded, up to date, and specific to a given knowledge base.
"""

reference_answer = """
Retrieval-augmented generation is an approach where a language model retrieves relevant information from external sources, such as documents or databases, and uses that information as context when generating a response. It is useful because it reduces reliance on the model's internal memory, improves factual grounding, enables domain-specific answers, and can make it easier to cite or inspect sources.
"""


def score_as_number(result: dict, field: str) -> float:
    """Convert a judge score to a number so we can aggregate it."""
    try:
        # JSON values may arrive as integers, floats, or numeric strings.
        return float(result[field])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Judge result is missing a numeric '{field}' score: {result}") from error


def run_judge(model: str, prompt: str) -> tuple[str, dict]:
    """Run one judge model and attach the model name to its parsed result."""
    # Tutorial 04 overrides the model for each call instead of relying only on
    # GROQ_MODEL from .env.
    raw_result = call_groq_llm(prompt, temperature=0.0, model=model)
    parsed_result = extract_json(raw_result)

    # Store the model name next to the result so the printed output is traceable.
    parsed_result["judge_model"] = model
    return raw_result, parsed_result


def average_scores(results: list[dict]) -> dict:
    """Average each rubric score across all successful judge results."""
    averages = {}

    for field in SCORE_FIELDS:
        # Average each criterion separately so students can see where judges agree
        # or disagree: accuracy may be high while completeness is lower.
        scores = [score_as_number(result, field) for result in results]
        averages[field] = round(mean(scores), 2)

    # Overall score is the average of each judge's three rubric scores.
    overall_scores = [
        mean(score_as_number(result, field) for field in SCORE_FIELDS)
        for result in results
    ]
    averages["overall"] = round(mean(overall_scores), 2)
    return averages


def majority_pass(results: list[dict]) -> dict:
    """Count how many judges give an average score at or above the threshold."""
    votes = []

    for result in results:
        # Each judge gets one vote based on its average rubric score.
        overall = mean(score_as_number(result, field) for field in SCORE_FIELDS)
        votes.append(overall >= PASS_THRESHOLD)

    pass_votes = sum(votes)
    fail_votes = len(votes) - pass_votes

    return {
        "pass_threshold": PASS_THRESHOLD,
        "pass_votes": pass_votes,
        "fail_votes": fail_votes,
        "majority_decision": "pass" if pass_votes > fail_votes else "needs_review",
    }


def main():
    # Reuse the same reference-based prompt from tutorial 01 so the only change
    # is the number of judge models.
    prompt = EVALUATION_PROMPT.format(
        question=question,
        response=assistant_response,
        reference=reference_answer,
    )

    print_header("Multiple LLM Judges")
    print("What this demonstrates: the same rubric can be judged by several models and then aggregated.")

    print_step(1, "Checking provider and judge ensemble")
    print_kv("Evaluation type", "multi-judge reference-based")
    print_kv("Provider", "groq")
    print("Judge models:")
    for model in JUDGE_MODELS:
        print(f"- {model}")

    print_step(2, "Inspecting multi-judge flow")
    print_ascii_tree(
        """
        Shared Question + Assistant Answer + Reference Answer
            |
            v
        Same Evaluation Prompt
            |
            +--> Judge Model 1 --> JSON scores
            +--> Judge Model 2 --> JSON scores
            +--> Judge Model 3 --> JSON scores
            |
            v
        Average Scores + Majority Vote
        """
    )

    print_step(3, "Reviewing inputs and rubric")
    print_kv("User question", question)
    print("\nAssistant response:")
    print(assistant_response.strip())
    print("\nReference answer:")
    print(reference_answer.strip())
    print("\nRubric: accuracy, relevance, completeness, each scored from 1 to 5.")
    print_prompt_preview(prompt, max_chars=900)

    results = []
    for index, model in enumerate(JUDGE_MODELS, start=4):
        print_step(index, f"Running judge model: {model}")

        # Run the same evaluation prompt through each model in the ensemble.
        raw_result, result = run_judge(model, prompt)
        results.append(result)
        print("Raw judge response:")
        print(raw_result)
        print("\nParsed JSON:")
        print_json(result)

    print_step(7, "Aggregating judge results")
    print("Average scores:")

    # Average scores are useful when you want a continuous measurement.
    averages = average_scores(results)
    print_json(averages)
    print("\nMajority decision:")

    # Majority voting is useful when you want a simple pass/fail style decision.
    decision = majority_pass(results)
    print_json(decision)

    print_step(8, "Final interpretation")
    print(f"Overall average: {averages['overall']}/5")
    print(f"Majority decision: {decision['majority_decision']}")
    print()
    print(
        "Using multiple judge models can reduce the risk that one model's style "
        "preferences dominate the evaluation. In production, this should still "
        "be calibrated against human ratings and known golden examples."
    )


if __name__ == "__main__":
    main()
