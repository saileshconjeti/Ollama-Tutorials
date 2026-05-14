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
import sys
from pathlib import Path

from ollama import chat

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import print_header, print_json, print_kv, print_step, print_text_preview

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

print_header("Structured Output with JSON Schema")
print("What this demonstrates: the model returns machine-readable fields instead of only prose.")
print_step(1, "Checking provider and model")
print_kv("Provider", "ollama")
print_kv("Model", "qwen3:4b")

print_step(2, "Inspecting input text and required schema")
print_text_preview("Input text", text, max_chars=500)
print_json(schema)

print_step(3, "Sending schema-constrained request to Ollama")
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
print_step(4, "Raw model response")
print(content)

print_step(5, "Parsed JSON")
parsed = json.loads(content)

print(json.dumps(parsed, indent=2))

print_step(6, "What to observe")
print("The parsed object has stable keys your application can use later for validation, storage, or routing.")
