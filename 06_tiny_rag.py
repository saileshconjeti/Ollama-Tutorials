# File name: 06_tiny_rag.py
# Purpose: Demonstrate a tiny end-to-end RAG pipeline and compare it against no-RAG answering.
# Concepts covered: RAG workflow, embeddings-based retrieval, cosine similarity, grounded prompting.
# Prerequisites: `ollama serve` running, models `qwen3:4b` and `qwen3-embedding:0.6b` pulled, `pip install ollama`.
# How to run: `python 06_tiny_rag.py`
# What students should observe: This script asks for a question, then shows no-RAG vs RAG answers side-by-side.
# Usage example:
#   python 06_tiny_rag.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import math
from ollama import chat, embed

# Small in-memory knowledge base used for retrieval in this teaching demo.
# In production, this would often come from a vector database or indexed document store.
documents = [
    """RAG stands for retrieval-augmented generation. In a RAG pipeline, the system first retrieves
relevant documents or chunks from a knowledge base. Those retrieved passages are then inserted into
the prompt as context before the language model generates its answer. This helps reduce hallucinations
and makes the answer more grounded in external information.""",

    """Embeddings convert text into numerical vectors. Texts with similar meaning usually have vectors
that are close together in embedding space. In RAG systems, embeddings are commonly used to compare
a user query with stored document chunks and retrieve the most semantically relevant passages.""",

    """Tool calling allows a language model to request the use of an external function or tool, such as
a calculator, weather API, search function, or database lookup. The model itself does not execute the
tool. Instead, the application detects the requested tool call, runs the tool in code, and sends the
tool result back to the model.""",

    """A good classroom use case for RAG is question answering over lecture notes. For example, a student
can ask, 'What is the difference between embeddings and fine-tuning?' The system retrieves the most
relevant lecture-note chunks and uses them as context so the answer is based on the course material
rather than only on the model's parametric memory.""",

    """Fine-tuning changes a model's behavior by training it further on additional examples. RAG is different.
RAG does not change the model weights. Instead, it supplies external information at inference time by
retrieving relevant documents and adding them to the prompt.""",

    """Chunking is an important design choice in RAG. If chunks are too small, important context may be split
apart. If chunks are too large, retrieval may become noisy because irrelevant text is bundled together.
Many practical systems use overlapping chunks so important facts are less likely to be separated.""",

    """One limitation of RAG is that retrieval quality determines answer quality. If the retriever selects
irrelevant chunks, the final answer may still be wrong. This is why evaluation of chunking strategy,
embedding model choice, and retrieval ranking is important in production RAG systems.""",

    """A useful mental model is:
1. user asks a question
2. embed the query
3. retrieve top matching chunks
4. place those chunks into the prompt
5. ask the language model to answer using that context
This is the core workflow of a simple RAG pipeline."""
]

# Utility: cosine similarity measures directional closeness between two vectors.
# Higher similarity generally means closer semantic meaning.
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

# Retrieval stage:
# 1) embed all documents
# 2) embed the user query
# 3) score each document with cosine similarity
# 4) return top-k matches
# Teaching note: retrieval quality affects final answer quality in RAG.
def retrieve(query, docs, embedding_model="qwen3-embedding:0.6b", top_k=3):
    doc_embeddings = embed(
        model=embedding_model,
        input=docs,
    )["embeddings"]

    query_embedding = embed(
        model=embedding_model,
        input=query,
    )["embeddings"][0]

    scored = []
    for i, (doc, emb) in enumerate(zip(docs, doc_embeddings), start=1):
        score = cosine_similarity(query_embedding, emb)
        scored.append((score, i, doc))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_k]

# Baseline path (no-RAG): answer directly from model memory without retrieved context.
def answer_without_rag(query, chat_model="qwen3:4b"):
    response = chat(
        model=chat_model,
        messages=[
            {
                "role": "system",
                "content": "You are a precise teaching assistant. Answer clearly and concisely."
            },
            {
                "role": "user",
                "content": query
            }
        ],
    )
    return response["message"]["content"]

# RAG path: inject retrieved context into the prompt and ask the model to answer from it.
# Students should observe that this answer is often more grounded and cites source docs.
def answer_with_rag(query, retrieved_docs, chat_model="qwen3:4b"):
    context_blocks = []
    for rank, (score, doc_id, doc_text) in enumerate(retrieved_docs, start=1):
        context_blocks.append(
            f"[Document {doc_id} | Rank {rank} | Similarity {score:.4f}]\n{doc_text}"
        )

    context = "\n\n".join(context_blocks)

    prompt = f"""
You are answering a question using retrieved context from a small course knowledge base.

Rules:
- Answer ONLY from the retrieved context below.
- If the answer is supported, give a concise explanation.
- Cite the supporting document numbers in your answer like [Document 3].
- If the retrieved context is insufficient, say exactly what is missing.
- Do not use outside knowledge.

Retrieved context:
{context}

Question:
{query}
"""

    response = chat(
        model=chat_model,
        messages=[
            {
                "role": "system",
                "content": "You are a precise teaching assistant. Use only the supplied retrieved context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return context, response["message"]["content"]

# Demo driver:
# - asks the user for a query (or uses a default)
# - runs no-RAG and RAG paths
# - prints retrieval evidence and both answers for comparison
if __name__ == "__main__":
    default_query = "What is the difference between RAG and fine-tuning?"
    user_query = input(
        f"Enter your question for the RAG demo\n"
        f"(press Enter to use default: '{default_query}'):\n> "
    ).strip()

    query = user_query if user_query else default_query

    print("\nRunning no-RAG answer...\n")
    no_rag_answer = answer_without_rag(query)

    print("Running retrieval...\n")
    retrieved = retrieve(query, documents, top_k=3)

    print("Running RAG-grounded answer...\n")
    context, rag_answer = answer_with_rag(query, retrieved)

    print("=" * 80)
    print("QUESTION:\n")
    print(query)

    print("\n" + "=" * 80)
    print("TOP RETRIEVED DOCUMENTS:\n")
    # Expected observation: top documents should usually be semantically related to the query.
    for score, doc_id, doc_text in retrieved:
        preview = doc_text.strip().replace("\n", " ")
        if len(preview) > 160:
            preview = preview[:160] + "..."
        print(f"Document {doc_id} | similarity={score:.4f}")
        print(f"Preview: {preview}\n")

    print("=" * 80)
    print("CONTEXT SENT TO MODEL (RAG):\n")
    print(context)

    print("\n" + "=" * 80)
    print("ANSWER WITHOUT RAG:\n")
    print(no_rag_answer)

    print("\n" + "=" * 80)
    print("ANSWER WITH RAG:\n")
    print(rag_answer)

    # Final teaching note reinforces the central RAG lesson:
    # better retrieval usually leads to better grounded answers.
    print("\n" + "=" * 80)
    print("TEACHING NOTE:\n")
    print(
        "Compare whether the RAG answer is more grounded, more specific, and cites the retrieved documents. "
        "If the retrieval corpus is weak or the wrong chunks are retrieved, the RAG answer may still be limited."
    )
