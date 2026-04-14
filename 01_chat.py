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

from ollama import chat

# This script demonstrates app usage of a local model:
# your Python code sends messages to Ollama and receives a structured response object.
response = chat(
    model="qwen3:4b",
    messages=[
        {"role": "system", "content": "You are a concise university teaching assistant."},
        {"role": "user", "content": "Explain RAG in 120 words."},
    ],
)

# Expected observation:
# the assistant content is plain text extracted from response["message"]["content"].
print(response["message"]["content"])
