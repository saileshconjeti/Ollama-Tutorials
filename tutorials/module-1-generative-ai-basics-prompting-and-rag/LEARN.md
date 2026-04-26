# LEARN - Generative AI Basics: Prompting and RAG

Module: **Module 1**

## Theory Goals

By the end of this class, students should be able to:

- explain how local LLM chat works in a Python loop
- distinguish single-turn from multi-turn interaction
- describe streaming responses and when they improve UX
- explain why structured output is useful in applications
- explain embeddings as semantic vectors
- explain the core RAG pipeline and why it reduces hallucinations
- differentiate RAG from tool calling and fine-tuning

## Concept Map

1. Prompting Basics
- Input prompt and model response
- Role instructions for consistency

2. Conversation State
- Why history matters
- How message arrays preserve context

3. Streaming
- Token-by-token output
- Better responsiveness for long answers

4. Structured Output
- JSON schema as contract
- Validation as a reliability layer

5. Embeddings
- Text to vectors
- Similar meaning -> closer vectors

6. RAG
- Retrieve relevant context first
- Generate grounded answer from retrieved context

## Key Distinctions

- RAG: injects external context at inference time
- Fine-tuning: changes model weights through training
- Tool calling: model requests external actions; app executes tools

## Files Covered

### Local Ollama Baseline Tutorials

- `01_chat.py`
- `02_multi_turn_chat.py`
- `03_streaming.py`
- `04_structured_output.py`
- `05_embeddings.py`
- `06_tiny_rag.py`

### Groq-Enabled Module 1 Variants

- `01_chat_groq.py`
- `02_multi_turn_chat_qroq.py`
- `03_streaming_groq.py`
- `04_structured_output_groq.py`
- `06_tiny_rag_qroq.py`

## Groq Workflow Notes

- Groq variants use the shared provider client at `tutorials/llm_client.py`.
- Students can switch providers per run using `--provider ollama` or `--provider groq`.
- `.env` keys for cloud mode:
  - `LLM_PROVIDER=groq`
  - `GROQ_API_KEY=...`
  - `GROQ_MODEL=llama-3.1-8b-instant`
- Embeddings lessons remain local in this module (`05_embeddings.py` and retrieval in `06_tiny_rag_qroq.py` still rely on Ollama embeddings).
- `Modelfile` (Personalized TA)
