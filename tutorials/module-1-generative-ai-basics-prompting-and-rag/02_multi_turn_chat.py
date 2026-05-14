# File name: 02_multi_turn_chat.py
# Purpose: Demonstrate multi-turn chat by sending conversation history in one request.
# Concepts covered: Conversation state, role-based messages, contextual responses.
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled, `pip install ollama`.
# How to run: `python 02_multi_turn_chat.py`
# What students should observe: The final answer reflects earlier turns in the message list.
# Usage example:
#   python 02_multi_turn_chat.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

from ollama import chat

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import print_header, print_json, print_kv, print_step

# In local model workflows, your application is responsible for conversation memory.
# Here, prior turns are explicitly included so the model can answer with context.
messages = [
    {"role": "system", "content": "You are a patient teaching assistant for a course on generative and agentic AI."},
    {"role": "user", "content": "What is RAG?"},
    {"role": "assistant", "content": "RAG stands for retrieval-augmented generation. It retrieves relevant information first, then uses that information to generate an answer."},
    {"role": "user", "content": "Give me a real classroom example."},
]

print_header("Multi-Turn Chat History")
print("What this demonstrates: conversation memory is represented by sending the previous turns again.")
print_step(1, "Checking provider and model")
print_kv("Provider", "ollama")
print_kv("Model", "qwen3:4b")

print_step(2, "Preparing conversation history")
print_json(messages)

print_step(3, "Sending full history to Ollama")
response = chat(
    model="qwen3:4b",
    messages=messages,
)

# Expected observation:
# the output should feel like a continuation of the prior classroom-style discussion.
print_step(4, "Assistant output received")
print(response["message"]["content"])

print_step(5, "What to observe")
print("The model can answer the last question because the earlier RAG explanation is included in the message list.")
