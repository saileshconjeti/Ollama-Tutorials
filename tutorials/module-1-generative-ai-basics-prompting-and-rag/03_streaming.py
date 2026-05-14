# File name: 03_streaming.py
# Purpose: Demonstrate token/chunk streaming from a local LLM call.
# Concepts covered: Streaming generation, incremental output, responsive UX.
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled, `pip install ollama`.
# How to run: `python 03_streaming.py`
# What students should observe: Text appears progressively, not all at once.
# Usage example:
#   python 03_streaming.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

from ollama import chat

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import print_header, print_json, print_kv, print_step

messages = [
    {"role": "user", "content": "Give me 10 short practical ideas for using local LLMs in education."}
]

print_header("Streaming Tokens from Ollama")
print("What this demonstrates: chunks are printed as soon as the model produces them.")
print_step(1, "Checking provider and model")
print_kv("Provider", "ollama")
print_kv("Model", "qwen3:4b")

print_step(2, "Preparing prompt")
print_json(messages)

print_step(3, "Opening stream and printing chunks")

# Streaming is an application-layer feature: your Python loop prints chunks as they arrive.
stream = chat(
    model="qwen3:4b",
    messages=messages,
    stream=True,
)

# Read each streamed chunk and print immediately for a real-time experience.
for chunk in stream:
    content = chunk.get("message", {}).get("content", "")
    print(content, end="", flush=True)

# End with a newline so the terminal prompt appears cleanly after streamed text.
print()

print_step(4, "What to observe")
print("Streaming improves perceived responsiveness because students see partial output before the full answer is complete.")
