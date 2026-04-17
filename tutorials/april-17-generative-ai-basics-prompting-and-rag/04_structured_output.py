# File name: 04_structured_output.py
# Purpose: Extract structured metadata from free text using a JSON schema.
# Concepts covered: Schema-constrained generation, structured output parsing, reliable downstream use.
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled, `pip install ollama`.
# How to run: `python 04_structured_output.py`
# What students should observe: The model returns JSON matching the required schema fields.
# Usage example:
#   python 04_structured_output.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import json
from ollama import chat

# The schema tells the model the shape of the response we want.
# This is useful when your app needs machine-readable fields instead of free-form prose.
schema = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "difficulty": {"type": "string"},
        "prerequisites": {
            "type": "array",
            "items": {"type": "string"}
        },
        "learning_objectives": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["course_title", "difficulty", "prerequisites", "learning_objectives"]
}

text = """
Course: Generative and Agentic AI Foundations
Level: Advanced Master's
Prerequisites: Python programming, machine learning basics, APIs
Goals: Understand prompting, local inference, RAG, tool calling, and agent design.
"""

# Request a schema-constrained extraction from the input text.
response = chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": f"Extract the course metadata from this text:\n\n{text}"
        }
    ],
    format=schema,
)

# Parse and print pretty JSON for easy inspection in class.
# Expected observation: keys required by the schema are present.
content = response["message"]["content"]
parsed = json.loads(content)

print(json.dumps(parsed, indent=2))
