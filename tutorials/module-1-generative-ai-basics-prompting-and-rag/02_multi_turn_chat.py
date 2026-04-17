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

from ollama import chat

# In local model workflows, your application is responsible for conversation memory.
# Here, prior turns are explicitly included so the model can answer with context.
messages = [
    {"role": "system", "content": "You are a patient teaching assistant for a course on generative and agentic AI."},
    {"role": "user", "content": "What is RAG?"},
    {"role": "assistant", "content": "RAG stands for retrieval-augmented generation. It retrieves relevant information first, then uses that information to generate an answer."},
    {"role": "user", "content": "Give me a real classroom example."},
]

response = chat(
    model="qwen3:4b",
    messages=messages,
)

# Expected observation:
# the output should feel like a continuation of the prior classroom-style discussion.
print(response["message"]["content"])
