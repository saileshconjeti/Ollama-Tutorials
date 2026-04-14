# Ollama Course (Python): Student README

Learn core local-LLM patterns with 7 short scripts: chat, multi-turn context, streaming, structured output, embeddings, tiny RAG, and tool calling.

## Author and Course Details

- Author: Dr. Sailesh Conjeti
- Course: Generative and Agentic AI
- Repository: https://github.com/saileshconjeti/Ollama-Tutorials
- Audience: Students learning practical local LLM workflows with Python and Ollama

---

## One-Page Quickstart (10-15 min)

### 1. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ollama
```

### 2. Start Ollama (keep this terminal running)
```bash
ollama serve
```

### 3. Pull required models (new terminal tab/window)
```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

### 4. Run all demos in order
```bash
python 01_chat.py
python 02_multi_turn_chat.py
python 03_streaming.py
python 04_structured_output.py
python 05_embeddings.py
python 06_tiny_rag.py
python 07_tool_calling.py
```

### 5. What to verify quickly
- `01`: you get a concise RAG explanation.
- `03`: text appears token-by-token (streaming), not all at once.
- `04`: pretty-printed JSON with course metadata fields.
- `05`: shows number of embeddings and vector dimension.
- `06`: prints both no-RAG and RAG answers plus retrieved docs/similarity.
- `07`: prints raw model message JSON; may include `tool_calls`.

---

## Repository Files Covered

- `01_chat.py`
- `02_multi_turn_chat.py`
- `03_streaming.py`
- `04_structured_output.py`
- `05_embeddings.py`
- `06_tiny_rag.py`
- `07_tool_calling.py`
- `Modelfile`

---

## Prerequisites

- Python 3.10+ recommended
- Ollama installed: https://ollama.com/download
- Terminal access

---

## Run in Order (Recommended Learning Path)

```bash
python 01_chat.py
python 02_multi_turn_chat.py
python 03_streaming.py
python 04_structured_output.py
python 05_embeddings.py
python 06_tiny_rag.py
python 07_tool_calling.py
```

---

## Script Guide (Time + What to Observe + Common Mistakes)

## `01_chat.py` (3-5 min)
**What it does**
- Sends one chat request to `qwen3:4b`.
- System: concise university teaching assistant.
- User: “Explain RAG in 120 words.”

**Run**
```bash
python 01_chat.py
```

**Observe**
- One final assistant response printed.

**Common mistakes**
- Model not pulled (`qwen3:4b` missing).
- Ollama server not running.

---

## `02_multi_turn_chat.py` (5 min)
**What it does**
- Sends a prebuilt multi-message history (system/user/assistant/user).
- Demonstrates how prior turns influence the next answer.

**Run**
```bash
python 02_multi_turn_chat.py
```

**Observe**
- Output should feel context-aware (classroom example of RAG).

**Common mistakes**
- Assuming this is interactive chat; it is fixed-message history in code.

---

## `03_streaming.py` (5 min)
**What it does**
- Uses `chat(..., stream=True)` and prints chunks as they arrive.

**Run**
```bash
python 03_streaming.py
```

**Observe**
- Text appears progressively, not after full completion.

**Common mistakes**
- Thinking output is broken because line buffering looks odd.
- Forgetting this script prints with `end=""` and flushes continuously.

---

## `04_structured_output.py` (8-10 min)
**What it does**
- Defines a JSON schema (`course_title`, `difficulty`, `prerequisites`, `learning_objectives`).
- Calls `chat(..., format=schema)`.
- Parses with `json.loads(...)` and pretty-prints JSON.

**Run**
```bash
python 04_structured_output.py
```

**Observe**
- Valid JSON object printed with required fields.

**Common mistakes**
- Assuming schema guarantees perfect output 100% of the time.
- JSON parse failure if model output is malformed in rare cases.

---

## `05_embeddings.py` (5 min)
**What it does**
- Calls `embed(...)` with `qwen3-embedding:0.6b` on 3 texts.
- Prints count and vector dimensionality.

**Run**
```bash
python 05_embeddings.py
```

**Observe**
- `Number of embeddings: 3`
- `Dimensions of first embedding: ...` (integer size)

**Common mistakes**
- Pulling only chat model and forgetting embedding model.

---

## `06_tiny_rag.py` (15-20 min)
**What it does**
- Uses an in-memory document list as a mini knowledge base.
- Embeds docs + query, computes cosine similarity, retrieves top 3 docs.
- Produces:
  - answer without RAG
  - RAG-grounded answer (grounded context + citation instruction)
- Script is interactive:
  - prompts for a question
  - pressing Enter uses default:  
    `What is the difference between RAG and fine-tuning?`
- Prints:
  - question
  - top retrieved docs + similarity
  - full context sent to model
  - answer without RAG
  - answer with RAG
  - teaching note

**Run**
```bash
python 06_tiny_rag.py
```

**Observe**
- Prompt asks for a question (Enter uses default).
- Prints top retrieved docs with similarity scores.
- Shows full context sent to model.
- Prints both no-RAG and RAG answers side-by-side.

**Common mistakes**
- Expecting persistent/vector DB storage (this script embeds in-memory every run).
- Assuming RAG is always better; poor retrieval can still limit answer quality.

---

## `07_tool_calling.py` (10-12 min)
**What it does**
- Registers one tool schema: `add_numbers(a, b)`.
- Sends “What is 37 + 58?”
- Prints raw model message JSON.
- If tool call exists:
  - app code executes addition (`a + b`)
  - app appends assistant tool-call message + tool result message
  - app calls `chat(...)` again for final natural-language answer
- If no tool call is returned:
  - prints “No tool call was requested...” and model text response.

**Run**
```bash
python 07_tool_calling.py
```

**Observe**
- Raw model object first.
- Either:
  - tool-call path with final answer, or
  - no-tool-call message path.

**Common mistakes**
- Thinking model executes Python tools itself.
- Skipping second round-trip after tool execution in app logic.

---

## No-RAG vs RAG in `06_tiny_rag.py`

**No-RAG**
- Model receives only the user question.
- Answer is from model’s internal knowledge.

**RAG**
- App retrieves top-matching local docs via embeddings + cosine similarity.
- Retrieved text is inserted into prompt as context.
- Model is instructed to answer only from retrieved context and cite document numbers.

**Student takeaway**
- RAG can improve grounding/specificity.
- Retrieval quality determines answer quality.

---

## Why `07_tool_calling.py` May Return Tool-Call Objects

In tool-calling mode, the model may return a tool request instead of final prose.  
That is expected and correct.

Flow:
1. Model returns `tool_calls` (function + args).
2. Application executes the tool in code.
3. Application sends tool output back as `role: "tool"`.
4. Model returns final user-facing answer.

Important: the model proposes tool use; your app performs it.

---

## `Modelfile` (Optional Extension, 5 min)

`Modelfile` defines:
- `FROM qwen3:4b`
- custom `SYSTEM` prompt
- `PARAMETER temperature 0.2`

Build custom model:
```bash
ollama create course-ta -f Modelfile
```

Try it:
```bash
ollama run course-ta "Explain RAG in 5 numbered steps."
```

Note: current Python scripts are hardcoded to `qwen3:4b`, not `course-ta`.

---

## Troubleshooting

## `ModuleNotFoundError: No module named 'ollama'`
```bash
source .venv/bin/activate
pip install ollama
```

## Cannot connect to Ollama / connection refused
```bash
ollama serve
```

## Model not found errors
```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

## `python` command not found
Use `python3`:
```bash
python3 01_chat.py
```

## `04_structured_output.py` JSON parsing error
- Retry run.
- Confirm model availability and server health.

## `06_tiny_rag.py` feels slow
- Embeddings are computed at runtime for all docs each run.

## `07_tool_calling.py` did not call tool
- This can happen; script intentionally handles both branches.

---

## Common Student Warnings (Read Before Lab)

- Run commands from the repository root.
- Keep Ollama server running while executing scripts.
- Activate `.venv` in every new terminal tab.
- Pull both chat and embedding models before starting.
- Do not assume these scripts maintain long-lived chat/session state across runs.
- `06_tiny_rag.py` is a teaching demo, not production RAG architecture.

---

## Suggested Lab Timing (Total: ~60-75 min)

1. Setup + model pulls: 10-15 min  
2. `01`-`03`: 15 min  
3. `04`-`05`: 15 min  
4. `06`: 15-20 min  
5. `07` + reflection: 10 min

---

## Credits

- Created and maintained by Dr. Sailesh Conjeti
- Course: Generative and Agentic AI
