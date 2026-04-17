# BUILD - Generative AI Basics: Prompting and RAG

Module: **Module 1**

## Prerequisites

- `ollama serve` is running
- Python virtual environment is active
- dependencies installed: `pip install -r requirements.txt`
- models available:
  - `qwen3:4b`
  - `qwen3-embedding:0.6b`
  - `qwen2.5:3b` (for personalized TA)

## Step-by-Step Execution

Run from repository root.

```bash
python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat.py
python tutorials/module-1-generative-ai-basics-prompting-and-rag/02_multi_turn_chat.py
python tutorials/module-1-generative-ai-basics-prompting-and-rag/03_streaming.py
python tutorials/module-1-generative-ai-basics-prompting-and-rag/04_structured_output.py
python tutorials/module-1-generative-ai-basics-prompting-and-rag/05_embeddings.py
python tutorials/module-1-generative-ai-basics-prompting-and-rag/06_tiny_rag.py
```

## Personalized TA Build

```bash
ollama create genai-course-ta -f tutorials/module-1-generative-ai-basics-prompting-and-rag/Modelfile
ollama run genai-course-ta
```

Suggested test prompt:

```text
Help me understand the difference between RAG and tool use with one practical example.
```

## Expected Student Observations

- scripts progress from simple prompting to grounded RAG
- structured outputs are easier to use in downstream code
- RAG answers should be more grounded than no-RAG answers
- personalized TA behavior is controlled by `Modelfile`
