# File name: 04_multiple_llm_judges.py
# Purpose: Run the same reference-based evaluation through multiple Groq models.
# How to run: python 04_multiple_llm_judges.py

import json
from statistics import mean

from utils.groq_client import call_groq_llm
from utils.json_utils import extract_json
from utils.prompts import EVALUATION_PROMPT


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


def run_judge(model: str, prompt: str) -> dict:
    """Run one judge model and attach the model name to its parsed result."""
    # Tutorial 04 overrides the model for each call instead of relying only on
    # GROQ_MODEL from .env.
    raw_result = call_groq_llm(prompt, temperature=0.0, model=model)
    parsed_result = extract_json(raw_result)

    # Store the model name next to the result so the printed output is traceable.
    parsed_result["judge_model"] = model
    return parsed_result


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

    print("\n=== Module 4 - AI Evals: LLM-as-a-Judge ===")
    print("Provider: groq | Models:")
    for model in JUDGE_MODELS:
        print(f"- {model}")
    print("\n=== 04 - Multiple LLM Judges for Reference-Based Evaluation ===")
    print("\nQuestion:")
    print(question)
    print("\nAssistant response:")
    print(assistant_response.strip())
    print("\nReference answer:")
    print(reference_answer.strip())

    results = []
    for model in JUDGE_MODELS:
        print(f"\nRunning judge model: {model}")

        # Run the same evaluation prompt through each model in the ensemble.
        result = run_judge(model, prompt)
        results.append(result)
        print(json.dumps(result, indent=2))

    print("\n=== Aggregated Judge Result ===")
    print("\nAverage scores:")

    # Average scores are useful when you want a continuous measurement.
    print(json.dumps(average_scores(results), indent=2))
    print("\nMajority decision:")

    # Majority voting is useful when you want a simple pass/fail style decision.
    print(json.dumps(majority_pass(results), indent=2))

    print("\nTeaching note:")
    print(
        "Using multiple judge models can reduce the risk that one model's style "
        "preferences dominate the evaluation. In production, this should still "
        "be calibrated against human ratings and known golden examples."
    )


if __name__ == "__main__":
    main()
