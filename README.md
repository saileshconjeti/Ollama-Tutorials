# Ollama Tutorials for Students (Mac + Python)

Practical, classroom-ready local LLM labs for **Generative and Agentic AI** using Ollama.

## Author and Course Details

- Author: **Dr. Sailesh Conjeti**
- Course: **Generative and Agentic AI**
- Repository: **https://github.com/saileshconjeti/Ollama-Tutorials**
- Audience: Students with Python basics and beginner-to-intermediate GenAI experience

---

## 0) Learning Outcomes

By the end of these practicals, students will be able to:

- install and verify Ollama on macOS
- run local chat models from CLI and Python
- understand multi-turn chat and streaming
- extract schema-constrained structured outputs
- generate embeddings and explain what vectors represent
- build a tiny RAG pipeline and compare no-RAG vs RAG behavior
- understand tool-calling flow where the **application executes tools**
- package a customized local assistant using a `Modelfile`

---

## 1) One-Page Quickstart (10-15 min)

### 1. Create and activate Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ollama
```

### 2. Start Ollama (keep running)

```bash
ollama serve
```

### 3. Pull required models for this repo

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

### 4. Run all tutorial scripts in order

```bash
python 01_chat.py
python 02_multi_turn_chat.py
python 03_streaming.py
python 04_structured_output.py
python 05_embeddings.py
python 06_tiny_rag.py
python 07_tool_calling.py
```

### 5. Quick observations checklist

- `01`: single local chat response
- `03`: output streams progressively
- `04`: valid JSON-like structured extraction behavior
- `05`: vector count + embedding dimension printed
- `06`: no-RAG and RAG answers shown side-by-side
- `07`: tool-call metadata may appear before final answer

---

## 2) Recommended Model Stack (M4 Pro-Friendly)

Use this stack for reliable classroom pace:

- `qwen3:4b` (primary teaching model)
- `llama3.2:3b` (comparison/fallback)
- `qwen3-embedding:0.6b` (embeddings + RAG)
- `qwen3:8b` (optional instructor-only stronger demo)

Pull optional comparison models:

```bash
ollama pull llama3.2:3b
ollama pull qwen3:8b
```

List installed models:

```bash
ollama list
```

---

## 3) Install and Verify Ollama on macOS

Typical flow:

1. Download Ollama DMG
2. Move Ollama to Applications
3. Launch Ollama
4. Verify CLI

Verify installation:

```bash
ollama --version
curl http://localhost:11434/api/tags
```

If `/api/tags` responds, local API is reachable.

---

## 4) Core CLI Commands Students Should Know

Run interactive chat:

```bash
ollama run qwen3:4b
```

List models:

```bash
ollama list
```

Show currently running models:

```bash
ollama ps
```

Stop a running model:

```bash
ollama stop qwen3:4b
```

Remove a model:

```bash
ollama rm qwen3:8b
```

---

## 5) Repository Files Covered

- `01_chat.py`
- `02_multi_turn_chat.py`
- `03_streaming.py`
- `04_structured_output.py`
- `05_embeddings.py`
- `06_tiny_rag.py`
- `07_tool_calling.py`
- `Modelfile`

---

## 6) Run in Order (Recommended Lab Sequence)

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

## 7) Script-by-Script Guide (Time + What to Observe)

## `01_chat.py` (3-5 min)

**Purpose**: first Python call to local Ollama chat.

Run:

```bash
python 01_chat.py
```

Observe:

- one final assistant reply printed from `response["message"]["content"]`
- difference between local model usage and app usage: your app sends structured messages and handles output

## `02_multi_turn_chat.py` (5 min)

**Purpose**: multi-turn context through a prebuilt message list.

Run:

```bash
python 02_multi_turn_chat.py
```

Observe:

- output depends on previous turns included in `messages`
- app code is responsible for conversation memory

## `03_streaming.py` (5 min)

**Purpose**: streaming token/chunk output.

Run:

```bash
python 03_streaming.py
```

Observe:

- text appears progressively (better UX for interactive apps)

## `04_structured_output.py` (8-10 min)

**Purpose**: schema-constrained extraction to machine-usable JSON.

Run:

```bash
python 04_structured_output.py
```

Observe:

- parsed JSON with expected fields (`course_title`, `difficulty`, etc.)
- why structured output matters: application-grade consistency vs free-form text

## `05_embeddings.py` (5 min)

**Purpose**: generate embeddings for multiple texts.

Run:

```bash
python 05_embeddings.py
```

Observe:

- one vector per input text
- embeddings are numeric vectors, **not answers**

## `06_tiny_rag.py` (15-20 min)

**Purpose**: compare no-RAG and RAG-grounded answers.

Run:

```bash
python 06_tiny_rag.py
```

Observe:

- script asks for a user query (Enter uses default)
- retrieval ranks documents by cosine similarity
- output includes:
  - top retrieved documents
  - context sent to model
  - answer without RAG
  - answer with RAG
- key lesson: retrieval quality affects answer quality

## `07_tool_calling.py` (10-12 min)

**Purpose**: demonstrate model-requested tools and application execution.

Run:

```bash
python 07_tool_calling.py
```

Observe:

- model may return tool-call objects first
- Python app executes the requested tool (`add_numbers`)
- app sends tool result back and then obtains final answer
- this is a core agentic loop pattern

---

## 8) No-RAG vs RAG (Important for `06_tiny_rag.py`)

**No-RAG path**

- model answers from its internal knowledge based only on user question

**RAG path**

- app embeds query and documents
- retrieves top relevant chunks
- injects retrieved context into prompt
- asks model to answer using retrieved context

**Teaching takeaway**

- RAG can increase grounding/specificity
- weak retrieval leads to weak final answers even with a strong model

---

## 9) Tool Calling Clarification (Important for `07_tool_calling.py`)

Tool calling does **not** mean the model executes Python by itself.

Actual flow:

1. user asks question
2. model requests a tool call (optional)
3. application executes tool function
4. application sends tool result as `role: "tool"`
5. model returns final answer

If step 3 is missing, tool-calling appears to “do nothing.”

---

## 10) Local API Practice with `curl`

Simple chat request:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:4b",
  "messages": [
    {"role": "user", "content": "Create 3 quiz questions about prompt engineering."}
  ],
  "stream": false
}'
```

Chat with system role:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:4b",
  "messages": [
    {"role": "system", "content": "You are a strict teaching assistant. Be concise."},
    {"role": "user", "content": "Explain RAG vs fine-tuning."}
  ],
  "stream": false
}'
```

Embeddings request:

```bash
curl http://localhost:11434/api/embed -d '{
  "model": "qwen3-embedding:0.6b",
  "input": "What is retrieval-augmented generation?"
}'
```

---

## 11) OpenAI-Compatible Local Endpoint (Bridge for Existing SDK Users)

Students familiar with OpenAI-style chat format can test locally:

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:4b",
    "messages": [
      {"role": "system", "content": "You are a concise teaching assistant."},
      {"role": "user", "content": "Explain tool calling in 3 bullet points."}
    ]
  }'
```

---

## 12) Optional JavaScript Track (Node.js)

Install client:

```bash
npm init -y
npm i ollama
```

`package.json` should include:

```json
{
  "type": "module"
}
```

`chat.js`:

```js
import ollama from 'ollama'

const response = await ollama.chat({
  model: 'qwen3:4b',
  messages: [
    { role: 'system', content: 'You are a concise teaching assistant.' },
    { role: 'user', content: 'Explain embeddings in 5 short bullet points.' }
  ]
})

console.log(response.message.content)
```

Run:

```bash
node chat.js
```

---

## 13) Build a Custom Course Assistant (`Modelfile`)

This repo includes a `Modelfile`.

Create model:

```bash
ollama create course-ta -f Modelfile
```

Run:

```bash
ollama run course-ta
```

Try prompt:

```text
Design a 15-minute classroom exercise to teach the difference between embeddings and chat models.
```

Note: Python scripts in this repo currently call `qwen3:4b` directly.

---

## 14) Troubleshooting

## `ollama: command not found`

- restart terminal after install
- verify Ollama app installed and CLI is available
- try `ollama --version`

## Cannot connect to `localhost:11434`

- Ollama service/app is not running
- start with `ollama serve` (or open Ollama app)

## Model not found

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

## Python package errors (`ModuleNotFoundError: ollama`)

```bash
source .venv/bin/activate
pip install ollama
```

## Slow model responses

- model may be too large for student hardware
- use smaller models (e.g., `llama3.2:3b`)
- first run can be slower due to model loading

## Messy output format

- use schema-constrained structured output (`04_structured_output.py`)

## Tool calling returned no final tool result

- model can request tool calls, but app must execute tool and return result
- see flow in `07_tool_calling.py`

## 15) Common Student Mistakes to Warn About

- forgetting to activate `.venv` in a new terminal tab
- pulling only chat model but not embedding model
- expecting embeddings to return natural-language answers
- assuming conversation memory persists automatically across script runs
- assuming tool-calling means automatic tool execution
- assuming RAG always improves quality regardless of retrieval quality

---

## Credits

- Created and maintained by **Dr. Sailesh Conjeti**
- Course: **Generative and Agentic AI**
