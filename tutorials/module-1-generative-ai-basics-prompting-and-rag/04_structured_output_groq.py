# File name: 04_structured_output_groq.py
# Purpose: Extract structured metadata from free text using a JSON schema with switchable provider (Ollama or Groq).
# Concepts covered: Schema-constrained generation, structured output parsing, reliable downstream use, local/cloud provider switching.
# Prerequisites: `pip install -r requirements.txt`; for Ollama mode, `ollama serve` and model pulled; for Groq mode, `GROQ_API_KEY` set.
# How to run: `python tutorials/module-1-generative-ai-basics-prompting-and-rag/04_structured_output_groq.py --provider ollama`
# What students should observe: The model returns JSON matching the required schema fields.
# Usage examples:
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/04_structured_output_groq.py --provider ollama
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/04_structured_output_groq.py --provider groq
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import json
import sys
from pathlib import Path

# Allow running this file directly via `python path/to/04_structured_output_groq.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import (
    get_selected_provider_and_model,
    parse_provider_from_cli,
    structured_chat,
)

provider = parse_provider_from_cli("Run a structured output example with Ollama or Groq.")
selected_provider, selected_model = get_selected_provider_and_model(provider)
print(f"Provider: {selected_provider} | Model: {selected_model}")

# The schema tells the model the shape of the response we want.
# This is useful when your app needs machine-readable fields instead of free-form prose.
schema = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "difficulty": {"type": "string"},
        "prerequisites": {
            "type": "array",
            "items": {"type": "string"},
        },
        "learning_objectives": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["course_title", "difficulty", "prerequisites", "learning_objectives"],
}

text = """
Course: Generative and Agentic AI Foundations
Level: Advanced Master's
Prerequisites: Python programming, machine learning basics, APIs
Goals: Understand prompting, local inference, RAG, tool calling, and agent design.
"""

# Request a schema-constrained extraction from the input text.
content = structured_chat(
    messages=[
        {
            "role": "user",
            "content": f"Extract the course metadata from this text:\n\n{text}",
        }
    ],
    schema=schema,
    provider=provider,
)

# Parse and print pretty JSON for easy inspection in class.
# Expected observation: keys required by the schema are present.
parsed = json.loads(content)
print(json.dumps(parsed, indent=2))
