# Reference-based evaluation prompt:
# The judge sees the question, the assistant response, and a reference answer.
# Double braces {{ and }} are required because the scripts use .format(...).
EVALUATION_PROMPT = """
You are evaluating an AI assistant's response.

USER QUESTION: {question}
ASSISTANT RESPONSE: {response}
REFERENCE ANSWER: {reference}

Score the response on each criterion from 1–5:

ACCURACY:
Does the response contain correct information?

RELEVANCE:
Does the response answer what was asked?

COMPLETENESS:
Does the response cover all necessary aspects?

A shorter response that fully addresses the query should score higher than a longer response with unnecessary detail.

Return JSON:
{{
  "accuracy": N,
  "relevance": N,
  "completeness": N,
  "reasoning": "brief explanation of scores"
}}
"""


# Pairwise evaluation prompt:
# The judge sees two candidate responses and chooses the better one.
# This is useful when there is no single perfect reference answer.
PAIRWISE_EVALUATION_PROMPT = """
You are evaluating two AI assistant responses to the same user question.

USER QUESTION:
{question}

RESPONSE A:
{response_a}

RESPONSE B:
{response_b}

Evaluate both responses using the following rubric:

1. Accuracy:
Does the response contain factually correct information?

2. Relevance:
Does the response directly answer the question?

3. Completeness:
Does the response cover the necessary aspects without adding unnecessary detail?

4. Clarity:
Is the response easy to understand?

Choose the better response.

Return JSON:
{{
  "winner": "A" or "B" or "tie",
  "score_a": N,
  "score_b": N,
  "reasoning": "brief explanation of the decision"
}}
"""
