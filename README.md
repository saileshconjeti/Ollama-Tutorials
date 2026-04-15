# Ollama Tutorials for Students (Python + Modelfile)

Practical, local LLM labs for **Generative and Agentic AI** using Ollama.

- Author: **Dr. Sailesh Conjeti**
- Course: **Generative and Agentic AI**
- Repository: **https://github.com/saileshconjeti/Ollama-Tutorials**

## Disclaimer

This material was prepared with assistance from **OpenAI Codex**, and every file in this repository has been manually reviewed and verified by the author before classroom use.

## What Students Will Learn

By completing this tutorial set, students will be able to:

- run local chat models from Python
- build multi-turn and streaming chat flows
- produce structured outputs from a schema
- generate embeddings and inspect vector dimensions
- implement a tiny end-to-end RAG pipeline
- implement tool calling where the **application executes tools**
- create and run a custom assistant from `Modelfile`

## Prerequisites

- Python 3.10+
- Ollama installed
- Terminal / Command Prompt access

## Setup by Operating System

### macOS

1. Install Ollama from the official website and launch the app once.
2. Verify installation:

```bash
ollama --version
```

3. In this project folder, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ollama
```

4. Start Ollama service (if not already running):

```bash
ollama serve
```

### Windows (PowerShell)

1. Install Ollama from the official website.
2. Verify installation in a new PowerShell window:

```powershell
ollama --version
```

3. In this project folder, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install ollama
```

4. Start Ollama service:

```powershell
ollama serve
```

If script execution is blocked, run PowerShell as user and set execution policy:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Linux

1. Install Ollama using the official install instructions for your distribution.
2. Verify installation:

```bash
ollama --version
```

3. In this project folder, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ollama
```

4. Start Ollama service:

```bash
ollama serve
```

## Pull Required Models

Run once on any OS:

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

Optional comparison model:

```bash
ollama pull llama3.2:3b
```

Check local models:

```bash
ollama list
```

## Low-Spec Machine Guidance

Default tutorial model: `qwen3:4b`

If student hardware is limited, use smaller chat models:

- `llama3.2:3b` (recommended first fallback)
- `qwen2.5:1.5b` (for very constrained systems)

Pull fallback models:

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:1.5b
```

Approximate RAM guidance for smooth classroom use:

- minimum workable: `8 GB RAM` (use `1.5b-3b` models)
- recommended baseline: `16 GB RAM` (`qwen3:4b` generally workable)
- comfortable for larger optional models: `24 GB+ RAM`

If responses are slow or the model is frequently unloaded, switch to a smaller model tag for the same script demonstrations.

## Run Tutorial Scripts (Python)

Run in order:

```bash
python 01_chat.py
python 02_multi_turn_chat.py
python 03_streaming.py
python 04_structured_output.py
python 05_embeddings.py
python 06_tiny_rag.py
python 07_tool_calling.py
```

## Tutorial Map

- `01_chat.py`: Minimal local chat call from Python
- `02_multi_turn_chat.py`: Conversation history and context
- `03_streaming.py`: Incremental token/chunk output
- `04_structured_output.py`: Schema-constrained JSON output
- `05_embeddings.py`: Embedding vectors and dimensions
- `06_tiny_rag.py`: Retrieval + grounded answering vs no-RAG
- `07_tool_calling.py`: Model requests tool, app executes tool

## Use the Included Modelfile

This repo includes a `Modelfile` for a custom course assistant.

Create model:

```bash
ollama create course-ta -f Modelfile
```

Run model:

```bash
ollama run course-ta
```

## Troubleshooting

### `ollama: command not found`

- restart terminal after installation
- verify Ollama was installed correctly

### Cannot connect to `localhost:11434`

- Ollama service/app is not running
- start with `ollama serve`

### `ModuleNotFoundError: ollama`

- activate virtual environment
- run `pip install ollama`

### Model not found

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

### Slow responses

- first run is slower because model loads into memory
- use smaller models for weaker hardware
