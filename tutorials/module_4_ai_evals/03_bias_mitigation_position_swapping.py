# File name: 03_bias_mitigation_position_swapping.py
# Purpose: Test whether a pairwise LLM judge is sensitive to answer order.
# How to run: python 03_bias_mitigation_position_swapping.py

import json

from utils.groq_client import call_groq_llm, get_selected_groq_model
from utils.json_utils import extract_json
from utils.prompts import PAIRWISE_EVALUATION_PROMPT


question = "What is the role of guardrails in AI agent systems?"

# Candidate 1 is stronger because it names concrete guardrail mechanisms and
# explains why agent systems create additional risk.
candidate_1 = """
Guardrails in AI agent systems are constraints, checks, and control mechanisms that help keep agent behavior safe, reliable, and aligned with user or system requirements. They can include input validation, output filtering, tool-use restrictions, human approval steps, policy checks, and monitoring. Guardrails are important because agents can take actions, call tools, and operate across multiple steps, which increases the risk of errors or unsafe behavior.
"""

# Candidate 2 is weaker because it is vague and treats guardrails as only prompts.
candidate_2 = """
Guardrails are basically prompts that make the AI behave nicely. They are useful because they tell the AI what to do.
"""


def run_pairwise_judge(response_a: str, response_b: str) -> dict:
    """Run one pairwise comparison and return the parsed judge result."""
    # The prompt only knows labels A and B. Later we map those labels back to
    # candidate_1 and candidate_2 so swapped order is still comparable.
    prompt = PAIRWISE_EVALUATION_PROMPT.format(
        question=question,
        response_a=response_a,
        response_b=response_b,
    )
    raw_result = call_groq_llm(prompt, temperature=0.0)
    return extract_json(raw_result)


def map_winner_to_candidate(judge_result: dict, candidate_for_a: str, candidate_for_b: str) -> str:
    """Translate winner labels A/B/tie back to stable candidate names."""
    # Normalize to lowercase so "A", "a", and similar outputs are handled.
    winner = str(judge_result.get("winner", "")).lower()

    if winner == "a":
        return candidate_for_a
    if winner == "b":
        return candidate_for_b
    if winner == "tie":
        return "tie"

    return "unknown"


def main():
    print("\n=== Module 4 - AI Evals: LLM-as-a-Judge ===")
    print(f"Provider: groq | Model: {get_selected_groq_model()}")
    print("\n=== 03 - Position Bias Test with Answer Swapping ===")
    print("\nQuestion:")
    print(question)
    print("\nCandidate 1:")
    print(candidate_1.strip())
    print("\nCandidate 2:")
    print(candidate_2.strip())

    # Run 1: stronger answer first, weaker answer second.
    original_order_result = run_pairwise_judge(candidate_1, candidate_2)
    original_order_winner = map_winner_to_candidate(
        original_order_result,
        candidate_for_a="candidate_1",
        candidate_for_b="candidate_2",
    )

    # Run 2: swap the answer positions, then map the winner back.
    # If the judge still chooses candidate_1, the result is less likely to be
    # caused by simply preferring the first or second position.
    swapped_order_result = run_pairwise_judge(candidate_2, candidate_1)
    swapped_order_winner = map_winner_to_candidate(
        swapped_order_result,
        candidate_for_a="candidate_2",
        candidate_for_b="candidate_1",
    )

    print("\nOriginal order judgment: candidate_1 as A, candidate_2 as B")
    print(json.dumps(original_order_result, indent=2))
    print(f"Mapped winner: {original_order_winner}")

    print("\nSwapped order judgment: candidate_2 as A, candidate_1 as B")
    print(json.dumps(swapped_order_result, indent=2))
    print(f"Mapped winner: {swapped_order_winner}")

    print("\nFinal interpretation:")
    # Stable result: the same candidate wins even after swapping answer order.
    if original_order_winner == swapped_order_winner and original_order_winner != "unknown":
        print(
            f"The result is more stable because {original_order_winner} won in both orders."
        )
    else:
        # Unstable result: this is a useful signal, not just a failure.
        print(
            "The winner changed or could not be mapped clearly. This may indicate "
            "position bias, ambiguous rubric interpretation, or judge instability."
        )


if __name__ == "__main__":
    main()
