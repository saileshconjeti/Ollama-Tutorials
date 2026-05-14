# File name: 03_bias_mitigation_position_swapping.py
# Purpose: Test whether a pairwise LLM judge is sensitive to answer order.
# How to run: python 03_bias_mitigation_position_swapping.py

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.groq_client import call_groq_llm, get_selected_groq_model
from utils.json_utils import extract_json
from utils.prompts import PAIRWISE_EVALUATION_PROMPT
from tutorials.terminal_utils import print_ascii_tree, print_header, print_json, print_kv, print_prompt_preview, print_step


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


def run_pairwise_judge(response_a: str, response_b: str) -> tuple[str, dict]:
    """Run one pairwise comparison and return the parsed judge result."""
    # The prompt only knows labels A and B. Later we map those labels back to
    # candidate_1 and candidate_2 so swapped order is still comparable.
    prompt = PAIRWISE_EVALUATION_PROMPT.format(
        question=question,
        response_a=response_a,
        response_b=response_b,
    )
    raw_result = call_groq_llm(prompt, temperature=0.0)
    return raw_result, extract_json(raw_result)


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
    print_header("Bias Check with Position Swapping")
    print("What this demonstrates: pairwise judges can be sensitive to answer order, so we swap A/B labels and compare.")

    print_step(1, "Checking provider and model")
    print_kv("Evaluation type", "bias check")
    print_kv("Provider", "groq")
    print_kv("Judge model", get_selected_groq_model())

    print_step(2, "Inspecting bias-check flow")
    print_ascii_tree(
        """
        Candidate 1 as A, Candidate 2 as B
            |
            v
        Judge Result 1

        Candidate 2 as A, Candidate 1 as B
            |
            v
        Judge Result 2
            |
            v
        Compare Mapped Winners
        """
    )

    print_step(3, "Reviewing question and candidates")
    print_kv("User question", question)
    print("\nCandidate 1:")
    print(candidate_1.strip())
    print("\nCandidate 2:")
    print(candidate_2.strip())

    # Run 1: stronger answer first, weaker answer second.
    original_prompt = PAIRWISE_EVALUATION_PROMPT.format(
        question=question,
        response_a=candidate_1,
        response_b=candidate_2,
    )
    print_step(4, "Running original order: candidate_1 as A, candidate_2 as B")
    print_prompt_preview(original_prompt, max_chars=700)
    original_raw_result, original_order_result = run_pairwise_judge(candidate_1, candidate_2)
    print("Raw judge response:")
    print(original_raw_result)
    print("\nParsed JSON:")
    print_json(original_order_result)
    original_order_winner = map_winner_to_candidate(
        original_order_result,
        candidate_for_a="candidate_1",
        candidate_for_b="candidate_2",
    )

    # Run 2: swap the answer positions, then map the winner back.
    # If the judge still chooses candidate_1, the result is less likely to be
    # caused by simply preferring the first or second position.
    swapped_prompt = PAIRWISE_EVALUATION_PROMPT.format(
        question=question,
        response_a=candidate_2,
        response_b=candidate_1,
    )
    print_step(5, "Running swapped order: candidate_2 as A, candidate_1 as B")
    print_prompt_preview(swapped_prompt, max_chars=700)
    swapped_raw_result, swapped_order_result = run_pairwise_judge(candidate_2, candidate_1)
    print("Raw judge response:")
    print(swapped_raw_result)
    print("\nParsed JSON:")
    print_json(swapped_order_result)
    swapped_order_winner = map_winner_to_candidate(
        swapped_order_result,
        candidate_for_a="candidate_2",
        candidate_for_b="candidate_1",
    )

    print_step(6, "Mapping A/B winners back to stable candidate names")
    print(f"Mapped winner: {original_order_winner}")
    print(f"Mapped winner: {swapped_order_winner}")

    print_step(7, "Final interpretation")
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
