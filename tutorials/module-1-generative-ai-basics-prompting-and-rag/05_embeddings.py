# File name: 05_embeddings.py
# Purpose: Show how to generate embeddings for multiple texts.
# Concepts covered: Semantic vectors, embedding models, vector shape inspection.
# Prerequisites: `ollama serve` running, model `qwen3-embedding:0.6b` pulled, `pip install ollama`.
# How to run: `python 05_embeddings.py`
# What students should observe: Embeddings are numeric vectors, not direct natural-language answers.
# Usage example:
#   python 05_embeddings.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import sys
from pathlib import Path

from ollama import embed

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import print_header, print_json, print_kv, print_step

# Embeddings map text into vector space so your application can compare meaning mathematically.
texts = [
    "RAG retrieves relevant documents before generation.",
    "Tool calling lets a model request actions from an application.",
    "Fine-tuning changes model behavior through additional training."
]

print_header("Text Embeddings")
print("What this demonstrates: text can be converted into vectors for similarity search and RAG retrieval.")
print_step(1, "Checking provider and model")
print_kv("Provider", "ollama")
print_kv("Embedding model", "qwen3-embedding:0.6b")

print_step(2, "Preparing texts to embed")
print_json(texts)

print_step(3, "Requesting embeddings")
# Generate one embedding vector per input text.
response = embed(
    model="qwen3-embedding:0.6b",
    input=texts,
)

# Expected observation:
# number of vectors equals number of input texts, and each vector has a fixed dimension.
print_step(4, "Inspecting vector output")
print(f"Number of embeddings: {len(response['embeddings'])}")
print(f"Dimensions of first embedding: {len(response['embeddings'][0])}")
print("First 8 numbers of the first vector:")
print(response["embeddings"][0][:8])

print_step(5, "What to observe")
print("Embeddings are numeric representations. We compare these vectors later to retrieve relevant chunks.")
