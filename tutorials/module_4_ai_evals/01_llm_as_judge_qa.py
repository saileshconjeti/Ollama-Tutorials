# File name: 01_llm_as_judge_qa.py
# Purpose: Evaluate one Q&A response against a reference answer using LLM-as-a-Judge.
# How to run: python 01_llm_as_judge_qa.py

import json

from utils.groq_client import call_groq_llm, get_selected_groq_model
from utils.json_utils import extract_json
from utils.prompts import EVALUATION_PROMPT


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
    print("\n=== Module 4 - AI Evals: LLM-as-a-Judge ===")
    print(f"Provider: groq | Model: {get_selected_groq_model()}")

    # Build the judge prompt by inserting the example question and answers.
    prompt = EVALUATION_PROMPT.format(
        question=question,
        response=assistant_response,
        reference=reference_answer,
    )

    # Ask the Groq-hosted LLM to act as the evaluator.
    raw_result = call_groq_llm(prompt, temperature=0.0)

    # Parse JSON so Python code can analyze the result programmatically.
    # We do this instead of only printing raw text because eval results are often
    # stored in spreadsheets, dashboards, or experiment logs.
    result = extract_json(raw_result)

    print("\n=== 01 - Reference-Based LLM-as-a-Judge Evaluation ===")
    print("\nQuestion:")
    print(question)
    print("\nAssistant response:")
    print(assistant_response.strip())
    print("\nReference answer:")
    print(reference_answer.strip())
    print("\nJudge result:")
    print(json.dumps(result, indent=2))
    print("\nTeaching note:")
    print(
        "This is a reference-based evaluation: the judge compares the assistant "
        "response against a known reference answer instead of relying on exact "
        "word matching."
    )


if __name__ == "__main__":
    main()
