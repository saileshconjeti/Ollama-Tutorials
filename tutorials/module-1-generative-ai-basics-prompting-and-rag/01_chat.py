# File name: 01_chat.py
# Purpose: Show the smallest possible local chat call from Python.
# Concepts covered: Local LLM inference, system vs user messages, application-driven prompting.
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled, `pip install ollama`.
# How to run: `python 01_chat.py`
# What students should observe: A single concise answer printed from the local model.
# Usage example:
#   python 01_chat.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

from ollama import chat

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import print_header, print_json, print_kv, print_step

# This script demonstrates app usage of a local model:
# your Python code sends messages to Ollama and receives a structured response object.
messages = [
    {"role": "system", "content": "You are a concise university teaching assistant for the course Generative and Agentic AI."},
    {"role": "user", "content": "Explain RAG in 120 words."},
]

print_header("Minimal Local Chat Call")
print("What this demonstrates: Python sends a system message and a user message to a local Ollama model.")

print_step(1, "Checking provider and model")
print_kv("Provider", "ollama")
print_kv("Model", "qwen3:4b")

print_step(2, "Preparing messages")
print_json(messages)

print_step(3, "Sending request to Ollama")
response = chat(
    model="qwen3:4b",
    messages=messages,
)

# Expected observation:
# the assistant content is plain text extracted from response["message"]["content"].
print_step(4, "Assistant output received")
print(response["message"]["content"])

print_step(5, "What to observe")
print("The application, not the model, decides which messages are sent and where the answer is printed.")
