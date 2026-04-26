# File name: 02_multi_turn_chat_qroq.py
# Purpose: Demonstrate multi-turn chat with switchable provider (Ollama or Groq).
# Concepts covered: Conversation state, role-based messages, contextual responses, local/cloud provider switching.
# Prerequisites: `pip install -r requirements.txt`; for Ollama mode, `ollama serve` and model pulled; for Groq mode, `GROQ_API_KEY` set.
# How to run: `python tutorials/module-1-generative-ai-basics-prompting-and-rag/02_multi_turn_chat_qroq.py --provider ollama`
# What students should observe: The final answer reflects earlier turns in the message list.
# Usage examples:
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/02_multi_turn_chat_qroq.py --provider ollama
#   python tutorials/module-1-generative-ai-basics-prompting-and-rag/02_multi_turn_chat_qroq.py --provider groq
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

# Allow running this file directly via `python path/to/02_multi_turn_chat_qroq.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.llm_client import chat, get_selected_provider_and_model, parse_provider_from_cli

provider = parse_provider_from_cli("Run a multi-turn chat example with Ollama or Groq.")
selected_provider, selected_model = get_selected_provider_and_model(provider)
print(f"Provider: {selected_provider} | Model: {selected_model}")

# In local/cloud model workflows, your application is responsible for conversation memory.
# Here, prior turns are explicitly included so the model can answer with context.
messages = [
    {"role": "system", "content": "You are a patient teaching assistant for a course on generative and agentic AI."},
    {"role": "user", "content": "What is RAG?"},
    {"role": "assistant", "content": "RAG stands for retrieval-augmented generation. It retrieves relevant information first, then uses that information to generate an answer."},
    {"role": "user", "content": "Give me a real classroom example."},
]

response = chat(
    messages=messages,
    provider=provider,
)

# Expected observation:
# the output should feel like a continuation of the prior classroom-style discussion.
print(response)
