# Ollama Tutorials for Students (Python + Personalized TA)

Practical LLM labs for **Generative and Agentic AI** using Ollama (local) and Groq (cloud).

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
- **Module 3**: [AI Agents](MODULE_3_AI_AGENTS.md)
  - Theory: [LEARN.md](tutorials/module-3-ai-agents/LEARN.md)
  - Code Walkthrough: [BUILD.md](tutorials/module-3-ai-agents/BUILD.md)

Module 2 now includes MCP + Notion integration tutorials:
- `13_mcp_list_tools.py`
- `14_mcp_direct_tool_call.py`
- `15_mcp_qwen_notion_writer.py`
- `15_mcp_groq_notion_writer.py`

## Repository Organization

- `tutorials/module-1-generative-ai-basics-prompting-and-rag/`
- `tutorials/module-2-workflow-patterns/`
- `tutorials/module-3-ai-agents/`
- `requirements.txt`
- `README.md`

This structure is designed to scale as new tutorial sets are added.

## System Requirements

- Python 3.10+
- Ollama (for local mode)
- Groq account + API key (optional, for cloud free-tier mode)
- Terminal or PowerShell
- Docker Desktop (recommended for Open WebUI)

## Setup by Operating System

Use one shared `.venv` and one shared root `requirements.txt` for all modules.
No module-specific requirements files are needed.

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

## Choose LLM Provider (Local Ollama or Groq Free Tier)

The new shared client at `tutorials/llm_client.py` supports both providers.

### Get a Groq API Key (students)

1. Go to the Groq Console and sign in.
2. Open the API Keys page.
3. Click `Create API Key`.
4. Copy the key once and store it safely (you may not be able to view it again).

### Mode A: Local Ollama (default)

1. Keep or set these in `.env` (optional because defaults are already set):

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
```

2. Make sure Ollama is running and the model exists:

```bash
ollama serve
ollama pull qwen3:4b
```

3. Run the cloud-ready tutorial variant:

```bash
python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat_groq.py
```

### Mode B: Groq Free-Tier Cloud

1. Add this to `.env`:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

2. Run any Groq-ready Module 1 tutorial:

```bash
python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat_groq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/02_multi_turn_chat_qroq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/03_streaming_groq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/04_structured_output_groq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/06_tiny_rag_qroq.py --provider groq
```

3. If you see a key error, confirm `.env` is in repo root and `GROQ_API_KEY` is valid.

For `06_tiny_rag_qroq.py`, embeddings are still local via Ollama. Keep Ollama running:

```bash
ollama serve
ollama pull qwen3-embedding:0.6b
```

Notes:
- `GROQ_MODEL=llama-3.1-8b-instant` is the default in `tutorials/llm_client.py`.
- You can switch providers any time by changing `LLM_PROVIDER` between `ollama` and `groq`.
- CLI `--provider` overrides `.env` for that single run.

### Important Limitation (RAG Embeddings)

For RAG embeddings, do not move embeddings to Groq. Keep embeddings local with Ollama (for example `qwen3-embedding:0.6b`) or switch to a small local embedding package.

Why:
- This module’s retrieval flow and embedding lessons are built around local embedding vectors.
- Keeping embeddings local ensures reproducible classroom behavior across all embedding and tiny-RAG tutorials.
- In this repository, Groq is the cloud replacement for chat generation/inference, not for `qwen3-embedding:0.6b`.

## MCP + Notion Environment (Module 2 Tutorials 13-15)

To run MCP tutorials in `tutorials/module-2-workflow-patterns/13-15`, add these to `.env`:

```dotenv
ZAPIER_MCP_URL=...
ZAPIER_MCP_API_KEY=...
NOTION_PARENT_PAGE_ID=...
```

Notes:
- `NOTION_PARENT_PAGE_ID` can be either a Notion page ID or a full Notion page URL (tutorial `14` normalizes both formats).
- Ensure the Zapier integration has access to that parent page in Notion (`Share` -> invite integration).

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
