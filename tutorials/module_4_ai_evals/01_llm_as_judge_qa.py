# File name: 01_llm_as_judge_qa.py
# Purpose: Evaluate one Q&A response against a reference answer using LLM-as-a-Judge.
# How to run: python 01_llm_as_judge_qa.py

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.groq_client import call_groq_llm, get_selected_groq_model
from utils.json_utils import extract_json
from utils.prompts import EVALUATION_PROMPT
from tutorials.terminal_utils import (
    print_ascii_tree,
    print_header,
    print_json,
    print_kv,
    print_prompt_preview,
    print_step,
)


# In a real eval dataset, each row would contain a question, model response,
# and reference answer. Here we keep one example so the flow is easy to inspect.
question = "What is retrieval-augmented generation, and why is it useful?"

# This is the answer we want to evaluate. It is mostly correct but shorter than
# the reference, which gives the judge a reason to think about completeness.
assistant_response = """
Retrieval-augmented generation, or RAG, is a technique where an AI system retrieves relevant external documents before generating an answer. It is useful because it can make answers more grounded, up to date, and specific to a given knowledge base.
"""

# The reference answer acts as the ground truth for this small demonstration.
reference_answer = """
Retrieval-augmented generation is an approach where a language model retrieves relevant information from external sources, such as documents or databases, and uses that information as context when generating a response. It is useful because it reduces reliance on the model's internal memory, improves factual grounding, enables domain-specific answers, and can make it easier to cite or inspect sources.
"""


def main():
    print_header("LLM-as-a-Judge Evaluation")
    print("What this demonstrates: a judge model scores one assistant answer against a reference answer.")

    print_step(1, "Checking provider and model")
    print_kv("Evaluation type", "reference-based")
    print_kv("Provider", "groq")
    print_kv("Judge model", get_selected_groq_model())

    print_step(2, "Inspecting evaluation data flow")
    print_ascii_tree(
        """
        User Question
            |
            v
        Assistant Response
            |
            v
        Reference Answer
            |
            v
        LLM-as-a-Judge Prompt
            |
            v
        Groq Judge Model
            |
            v
        Structured JSON Scores
        """
    )

    print_step(3, "Reviewing inputs and rubric")
    print_kv("User question", question)
    print("\nAssistant answer:")
    print(assistant_response.strip())
    print("\nReference answer:")
    print(reference_answer.strip())
    print("\nRubric: accuracy, relevance, completeness, each scored from 1 to 5.")

    # Build the judge prompt by inserting the example question and answers.
    prompt = EVALUATION_PROMPT.format(
        question=question,
        response=assistant_response,
        reference=reference_answer,
    )
    print_step(4, "Preparing judge prompt")
    print_prompt_preview(prompt, max_chars=900)

    # Ask the Groq-hosted LLM to act as the evaluator.
    print_step(5, "Sending request to Groq")
    raw_result = call_groq_llm(prompt, temperature=0.0)
    print("Raw judge response:")
    print(raw_result)

    # Parse JSON so Python code can analyze the result programmatically.
    # We do this instead of only printing raw text because eval results are often
    # stored in spreadsheets, dashboards, or experiment logs.
    print_step(6, "Parsing JSON response")
    result = extract_json(raw_result)
    print_json(result)

    print_step(7, "Interpreting scores")
    for field in ("accuracy", "relevance", "completeness"):
        print(f"{field.title()}: {result.get(field, '[missing]')}/5")
    print(f"Reasoning: {result.get('reasoning', '[missing]')}")
    print()
    print(
        "This is a reference-based evaluation: the judge compares the assistant "
        "response against a known reference answer instead of relying on exact "
        "word matching."
    )


if __name__ == "__main__":
    main()
