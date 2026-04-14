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

from ollama import chat

# Streaming is an application-layer feature: your Python loop prints chunks as they arrive.
stream = chat(
    model="qwen3:4b",
    messages=[
        {"role": "user", "content": "Give me 10 short practical ideas for using local LLMs in education."}
    ],
    stream=True,
)

# Read each streamed chunk and print immediately for a real-time experience.
for chunk in stream:
    content = chunk.get("message", {}).get("content", "")
    print(content, end="", flush=True)

# End with a newline so the terminal prompt appears cleanly after streamed text.
print()
