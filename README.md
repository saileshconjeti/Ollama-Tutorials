# Ollama Tutorials for Students (Python + Personalized TA)

Practical local LLM labs for **Generative and Agentic AI** using Ollama, plus a personalized Teaching Assistant (TA) built with `Modelfile` and Open WebUI.

- Author: **Dr. Sailesh Conjeti**
- Course: **Generative and Agentic AI**
- Repository: **https://github.com/saileshconjeti/Ollama-Tutorials**

## Disclaimer

This material was prepared with assistance from **OpenAI Codex**, and every file in this repository has been manually reviewed and verified by the author before classroom use.

## Repo Contents

- `01_chat.py` to `07_tool_calling.py`: Python tutorial labs
- `Modelfile`: personalized course TA model recipe
- `README.md`: setup + lab instructions

## Learning Outcomes

By completing this repository, students will be able to:

- run local chat models from Python
- build multi-turn and streaming chat workflows
- extract structured outputs using schemas
- generate embeddings and understand vector dimensions
- implement a tiny RAG pipeline
- implement application-side tool calling
- build and personalize a local course TA with `Modelfile`
- use Open WebUI as a local browser interface for their TA

## System Requirements

- Python 3.10+
- Ollama
- Terminal or PowerShell
- Docker Desktop (recommended for Open WebUI)

### Model and RAM Guidance

Use this default classroom stack:

- default model: `qwen2.5:3b`
- low-end fallback: `qwen2.5:1.5b` or `llama3.2:1b`
- optional coding helper: `qwen2.5-coder:1.5b`

Recommended RAM:

- minimum workable: `8 GB` (prefer `1.5b` to `3b` models)
- recommended baseline: `16 GB` (`qwen2.5:3b` works more reliably)
- comfortable headroom: `24 GB+`

## Setup by Operating System

### macOS

1. Install Ollama from the official download page and launch it once.
2. Verify:

```bash
ollama --version
```

3. Create Python environment in this project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ollama
```

4. Start Ollama if needed:

```bash
ollama serve
```

### Windows (PowerShell)

1. Install Ollama from the official download page.
2. Verify:

```powershell
ollama --version
```

3. Create Python environment in this project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install ollama
```

4. Start Ollama if needed:

```powershell
ollama serve
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Linux

1. Install Ollama using official Linux instructions.
2. Verify:

```bash
ollama --version
```

3. Create Python environment in this project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ollama
```

4. Start Ollama if needed:

```bash
ollama serve
```

## Pull Models

For Python labs in this repo:

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

For personalized TA exercise:

```bash
ollama pull qwen2.5:3b
ollama pull qwen2.5:1.5b
ollama pull llama3.2:1b
ollama pull qwen2.5-coder:1.5b
```

Check installed models:

```bash
ollama list
```

## Python Tutorial Track

Run scripts in order:

```bash
python 01_chat.py
python 02_multi_turn_chat.py
python 03_streaming.py
python 04_structured_output.py
python 05_embeddings.py
python 06_tiny_rag.py
python 07_tool_calling.py
```

## Personalized TA Exercise (Modelfile)

This repo includes a ready `Modelfile` that defines:

- base model: `qwen2.5:3b`
- low-temperature classroom behavior
- clear TA policy (hints, scaffolding, no assignment substitution)

### Build and Test the TA Model

```bash
ollama create genai-course-ta -f Modelfile
ollama run genai-course-ta
```

Try prompt:

```text
I am a student in a practical course on generative and agentic AI. Help me understand the difference between RAG and tool use.
```

### Personalize the TA

Students can edit `Modelfile` and rebuild:

```bash
ollama create genai-course-ta -f Modelfile
```

Common personalization ideas:

- more concise default answers
- stronger debugging focus
- more guided hints and checkpoints
- course/project-specific style instructions

## Open WebUI Setup (Student Laptop)

Recommended approach:

- run Ollama natively on the host
- run Open WebUI in Docker

This keeps model inference in Ollama while giving students a browser UI.

### 1) Install Docker Desktop

Install Docker Desktop (macOS/Windows), open it, then verify:

```bash
docker --version
```

### 2) Run Open WebUI Container

```bash
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

Open:

`http://localhost:3000`

### 3) Connect Open WebUI to Ollama

In Open WebUI:

1. Admin Settings
2. Connections
3. Ollama
4. Set endpoint

If Open WebUI runs in Docker and Ollama runs on host, use:

`http://host.docker.internal:11434`

### 4) Use the Custom TA in Open WebUI

After connection, select `genai-course-ta` as model.

### 5) Add Student Knowledge

Students should upload:

- lecture slides
- lab sheets
- personal notes
- rubric summaries

Then attach these to their model/preset for grounded help.

### 6) Security Note for Classrooms

In early weeks, avoid enabling unreviewed tools/plugins in Open WebUI. Focus first on chat + knowledge workflow.

## Daily Commands for Students

```bash
ollama serve
ollama list
ollama run genai-course-ta
ollama show --modelfile genai-course-ta
docker start open-webui
docker stop open-webui
```

Remove UI container but keep persisted data volume:

```bash
docker rm -f open-webui
```

## Troubleshooting

### `ollama: command not found`

- restart terminal
- relaunch Ollama app
- recheck `ollama --version`

### Open WebUI opens but models do not appear

- ensure Ollama is running
- verify Ollama endpoint in Open WebUI
- for Docker Open WebUI + host Ollama: use `http://host.docker.internal:11434`

### Model responses are too slow

- switch from `qwen2.5:3b` to `qwen2.5:1.5b` or `llama3.2:1b`
- reduce context (`PARAMETER num_ctx 4096`) in `Modelfile` if needed

### Python error: `ModuleNotFoundError: ollama`

```bash
# macOS/Linux
source .venv/bin/activate
pip install ollama
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install ollama
```
