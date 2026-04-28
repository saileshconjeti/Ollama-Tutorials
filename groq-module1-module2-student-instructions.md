# Updated Instructions: Groq Cloud Variants for Module 1 and Module 2

To support students with limited local compute, we will use Groq cloud variants for Module 1 and Module 2. This should make the labs smoother on lower-spec laptops.

At the time of writing, Groq's free tier (around 500K tokens/day) is typically enough for classroom experimentation.

Course repository:
https://github.com/saileshconjeti/Ollama-Tutorials

## 1) Read the module guides

- Module 1 `BUILD.md`:
https://github.com/saileshconjeti/Ollama-Tutorials/blob/main/tutorials/module-1-generative-ai-basics-prompting-and-rag/BUILD.md
- Module 1 `LEARN.md`:
https://github.com/saileshconjeti/Ollama-Tutorials/blob/main/tutorials/module-1-generative-ai-basics-prompting-and-rag/LEARN.md
- Module 2 `BUILD.md`:
https://github.com/saileshconjeti/Ollama-Tutorials/blob/main/tutorials/module-2-workflow-patterns/BUILD.md
- Module 2 `LEARN.md`:
https://github.com/saileshconjeti/Ollama-Tutorials/blob/main/tutorials/module-2-workflow-patterns/LEARN.md

## 2) Environment setup (from repo root)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For every new terminal session:

```bash
source .venv/bin/activate
```

## 3) Create a Groq API key

1. Go to: https://console.groq.com/
2. Open `API Keys` and create a new key.
3. Copy it for your `.env` file.

## 4) Create/update `.env` in repo root

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Do not commit `.env` or share your API key.

## 5) Module 1 (Groq variants)

```bash
python tutorials/module-1-generative-ai-basics-prompting-and-rag/01_chat_groq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/02_multi_turn_chat_qroq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/03_streaming_groq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/04_structured_output_groq.py --provider groq
python tutorials/module-1-generative-ai-basics-prompting-and-rag/05_embeddings.py
python tutorials/module-1-generative-ai-basics-prompting-and-rag/06_tiny_rag_qroq.py --provider groq
```

Note: embeddings steps still use local Ollama.

## 6) Module 2 (Groq variants)

```bash
python tutorials/module-2-workflow-patterns/08_prompt_chaining_groq.py --provider groq --file tutorials/module-2-workflow-patterns/sample_meeting_minutes.txt --output tutorials/module-2-workflow-patterns/my_minutes_report.md
python tutorials/module-2-workflow-patterns/09_routing_groq.py --provider groq
python tutorials/module-2-workflow-patterns/10_orchestrator_worker_groq.py --provider groq
python tutorials/module-2-workflow-patterns/11_evaluator_reflection_groq.py --provider groq
python tutorials/module-2-workflow-patterns/12_tool_calling_groq.py --provider groq
python tutorials/module-2-workflow-patterns/15_mcp_groq_notion_writer.py
```

For MCP/Notion scripts (`13-15`), also include in `.env`:

```dotenv
ZAPIER_MCP_URL=...
ZAPIER_MCP_API_KEY=...
NOTION_PARENT_PAGE_ID=...
```

## If you hit an error

Send:

1. The exact command you ran
2. Full terminal error output
3. A screenshot of `.env` keys with secrets masked (show only first/last 3 characters)
