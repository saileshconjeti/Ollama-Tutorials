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

from ollama import embed

# Embeddings map text into vector space so your application can compare meaning mathematically.
texts = [
    "RAG retrieves relevant documents before generation.",
    "Tool calling lets a model request actions from an application.",
    "Fine-tuning changes model behavior through additional training."
]

# Generate one embedding vector per input text.
response = embed(
    model="qwen3-embedding:0.6b",
    input=texts,
)

# Expected observation:
# number of vectors equals number of input texts, and each vector has a fixed dimension.
print(f"Number of embeddings: {len(response['embeddings'])}")
print(f"Dimensions of first embedding: {len(response['embeddings'][0])}")
