# Ollama Tutorials for Students (Python + Personalized TA)

Practical local LLM labs for **Generative and Agentic AI** using Ollama.

- Author: **Dr. Sailesh Conjeti**
- Course: **Generative and Agentic AI**
- Repository: **https://github.com/saileshconjeti/Ollama-Tutorials**

## Disclaimer

This material was prepared with assistance from **OpenAI Codex**, and every file in this repository has been manually reviewed and verified by the author before classroom use.

## Class Schedule and Guides

- **Module 1**: [Generative AI Basics - Prompting and RAG](MODULE_1_GENERATIVE_AI_BASICS_PROMPTING_AND_RAG.md)
  - Theory: [LEARN.md](tutorials/module-1-generative-ai-basics-prompting-and-rag/LEARN.md)
  - Code Walkthrough: [BUILD.md](tutorials/module-1-generative-ai-basics-prompting-and-rag/BUILD.md)
- **Module 2**: [Workflow Patterns](MODULE_2_WORKFLOW_PATTERNS.md)
  - Theory: [LEARN.md](tutorials/module-2-workflow-patterns/LEARN.md)
  - Code Walkthrough: [BUILD.md](tutorials/module-2-workflow-patterns/BUILD.md)

## Repository Organization

- `tutorials/module-1-generative-ai-basics-prompting-and-rag/`
- `tutorials/module-2-workflow-patterns/`
- `requirements.txt`
- `README.md`

This structure is designed to scale as new tutorial sets are added.

## System Requirements

- Python 3.10+
- Ollama
- Terminal or PowerShell
- Docker Desktop (recommended for Open WebUI)

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
pip install -r requirements.txt
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
pip install -r requirements.txt
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
pip install -r requirements.txt
```

4. Start Ollama if needed:

```bash
ollama serve
```

## Pull Models

For these tutorials:

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

For personalized TA exercises:

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

## Open WebUI Setup (Optional)

Recommended approach:

- run Ollama natively on host
- run Open WebUI in Docker

```bash
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

Open:

`http://localhost:3000`

If Open WebUI runs in Docker and Ollama runs on host, use this Ollama endpoint in WebUI settings:

`http://host.docker.internal:11434`
