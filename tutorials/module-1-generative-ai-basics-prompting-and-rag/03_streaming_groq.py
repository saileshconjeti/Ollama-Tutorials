# File name: 03_streaming_groq.py
# Purpose: Demonstrate token/chunk streaming with switchable provider (Ollama or Groq).
# Concepts covered: Streaming generation, incremental output, responsive UX, local/cloud provider switching.
# Prerequisites: `pip install -r requirements.txt`; for Ollama mode, `ollama serve` and model pulled; for Groq mode, `GROQ_API_KEY` set.
# How to run: `python tutorials/module-1-generative-ai-basics-prompting-and-rag/03_streaming_groq.py --provider ollama`
# What students should observe: Text appears progressively, not all at once.
# Usage examples:
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/03_streaming_groq.py --provider ollama
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/03_streaming_groq.py --provider groq
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

# Allow running this file directly via `python path/to/03_streaming_groq.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import (
    get_selected_provider_and_model,
    parse_provider_from_cli,
    stream_chat,
)
from tutorials.terminal_utils import print_header, print_json, print_kv, print_step

provider = parse_provider_from_cli("Run a streaming chat example with Ollama or Groq.")
selected_provider, selected_model = get_selected_provider_and_model(provider)
messages = [
    {"role": "user", "content": "Give me 10 short practical ideas for using local LLMs in education."}
]

print_header("Streaming with Provider Switching")
print("What this demonstrates: both local and cloud providers can stream partial text.")
print_step(1, "Checking provider and model")
print_kv("Provider", selected_provider)
print_kv("Model", selected_model)

print_step(2, "Preparing prompt")
print_json(messages)

print_step(3, f"Opening stream from {selected_provider}")

# Streaming is an application-layer feature: your Python loop prints chunks as they arrive.
stream = stream_chat(
    messages=messages,
    provider=provider,
)

# Read each streamed chunk and print immediately for a real-time experience.
for content in stream:
    print(content, end="", flush=True)

# End with a newline so the terminal prompt appears cleanly after streamed text.
print()

print_step(4, "What to observe")
print("The loop prints each chunk immediately; the final answer is assembled visually in the terminal.")
