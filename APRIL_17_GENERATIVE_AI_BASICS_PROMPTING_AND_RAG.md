# Generative AI Basics - Prompting and RAG

Date: **April 17, 2026**

## Learning Materials

- Theory: [LEARN.md](tutorials/april-17-generative-ai-basics-prompting-and-rag/LEARN.md)
- Code Walkthrough: [BUILD.md](tutorials/april-17-generative-ai-basics-prompting-and-rag/BUILD.md)

## What We Covered Today

- `01_chat.py`: Basic chat call from Python
- `02_multi_turn_chat.py`: Multi-turn conversation state
- `03_streaming.py`: Streaming responses
- `04_structured_output.py`: Structured JSON output with schema validation
- `05_embeddings.py`: Embeddings and vector intuition
- `06_tiny_rag.py`: End-to-end tiny RAG demo
- `Modelfile`: Personalized Teaching Assistant (TA)

## Run Order (Today)

From repo root:

```bash
python tutorials/april-17-generative-ai-basics-prompting-and-rag/01_chat.py
python tutorials/april-17-generative-ai-basics-prompting-and-rag/02_multi_turn_chat.py
python tutorials/april-17-generative-ai-basics-prompting-and-rag/03_streaming.py
python tutorials/april-17-generative-ai-basics-prompting-and-rag/04_structured_output.py
python tutorials/april-17-generative-ai-basics-prompting-and-rag/05_embeddings.py
python tutorials/april-17-generative-ai-basics-prompting-and-rag/06_tiny_rag.py
```

## Personalized TA (Covered Today)

Build and run from repo root:

```bash
ollama create genai-course-ta -f tutorials/april-17-generative-ai-basics-prompting-and-rag/Modelfile
ollama run genai-course-ta
```

Suggested prompt:

```text
I am a student in a practical course on generative and agentic AI. Help me understand the difference between RAG and tool use.
```

## Learning Focus

- Understand core local LLM interaction patterns
- Compare plain prompting vs retrieval-augmented prompting
- Learn where structured output is useful
- Build a reusable personalized TA baseline
