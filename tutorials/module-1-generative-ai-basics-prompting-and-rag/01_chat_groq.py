# File name: 01_chat_groq.py
# Purpose: Show the smallest possible chat call with switchable provider (Ollama or Groq).
# Concepts covered: Local/cloud LLM inference, system vs user messages, application-driven prompting.
# Prerequisites: `pip install -r requirements.txt`; for Ollama mode, `ollama serve` and model pulled; for Groq mode, `GROQ_API_KEY` set.
# How to run: `python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat_groq.py --provider ollama`
# What students should observe: A single concise answer printed from the configured provider.
# Usage examples:
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat_groq.py --provider ollama
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat_groq.py --provider groq
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

# Allow running this file directly via `python path/to/01_chat_groq.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import chat, get_selected_provider_and_model, parse_provider_from_cli
from tutorials.terminal_utils import print_header, print_json, print_kv, print_step


provider = parse_provider_from_cli("Run a minimal chat example with Ollama or Groq.")
selected_provider, selected_model = get_selected_provider_and_model(provider)
print_header("Minimal Chat Call with Provider Switching")
print("What this demonstrates: the same message list can be sent to Ollama locally or Groq in the cloud.")
print_step(1, "Checking provider and model")
print_kv("Provider", selected_provider)
print_kv("Model", selected_model)

# This script demonstrates app usage of a switchable model provider:
# your Python code sends messages and receives assistant text from Ollama (default) or Groq.
messages = [
    {"role": "system", "content": "You are a concise university teaching assistant for the course Generative and Agentic AI."},
    {"role": "user", "content": "Explain Retrieval Augmented Generation in 120 words."},
]
print_step(2, "Preparing messages")
print_json(messages)

print_step(3, f"Sending request to {selected_provider}")
response = chat(
    messages=messages,
    temperature=0.2,
    provider=provider,
)

print_step(4, "Assistant output received")
print(response)

print_step(5, "What to observe")
print("Changing --provider changes the backend, while the prompt and Python control flow stay the same.")
