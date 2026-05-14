# File name: workflow_utils.py
# Purpose: Shared helpers for the workflow-pattern tutorials.
# Concepts covered: Ollama structured output, schema validation, retry, JSON fallback parsing.
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled,
#                `pip install -r requirements.txt`
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI
#
# Used across module-2 scripts including:
# - 08-12 for core workflow patterns
# - 15 for Qwen structured generation before MCP-based Notion writing

from __future__ import annotations

import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, Type, TypeVar

from dotenv import load_dotenv
from groq import BadRequestError, Groq
from ollama import chat as ollama_chat
from pydantic import BaseModel, ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tutorials.terminal_utils import (
    print_actionable_error,
    print_ascii_tree,
    print_header,
    print_json,
    print_prompt_preview,
    print_step,
    print_substep,
)

T = TypeVar("T", bound=BaseModel)

load_dotenv()

DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
DEFAULT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen3:4b")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def print_subheader(title: str) -> None:
    """Print a smaller section header."""
    print_substep(title)


def pretty_json(data: Any) -> str:
    """Return nicely formatted JSON for printing."""
    if isinstance(data, BaseModel):
        return json.dumps(data.model_dump(), indent=2)
    return json.dumps(data, indent=2)


def extract_json_block(text: str) -> str:
    """
    Try to extract the first JSON object or array from model output.

    This is a fallback for cases where the model returns extra prose
    around otherwise valid JSON.
    """
    text = text.strip()

    # If it already looks like JSON, return as-is.
    if text.startswith("{") or text.startswith("["):
        return text

    match = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
    if match:
        return match.group(1)

    raise ValueError("Could not find a JSON block in model output.")


def _looks_like_ollama_model(model: str) -> bool:
    """Heuristic: Ollama model names commonly include a colon tag."""
    return ":" in model


def _resolve_provider(provider: str | None) -> str:
    selected = (provider or DEFAULT_PROVIDER).lower()
    if selected not in {"ollama", "groq"}:
        return "ollama"
    return selected


def _resolve_model_for_provider(provider: str, model: str) -> str:
    """
    Keep existing Module-2 defaults working across providers.
    If Groq is selected but an Ollama-style model name is passed,
    use GROQ_MODEL unless the caller supplied a Groq-style name.
    """
    if provider == "groq" and _looks_like_ollama_model(model):
        return DEFAULT_GROQ_MODEL
    return model


def _call_text(
    *,
    messages: list[dict[str, str]],
    provider: str,
    model: str,
) -> str:
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            print_actionable_error(
                "GROQ_API_KEY was not found.",
                "This workflow is using Groq as the cloud LLM provider.",
                [
                    "Create a .env file in the project root.",
                    "Add GROQ_API_KEY=your_key_here.",
                    "Re-run with --provider groq, or use --provider ollama for local inference.",
                ],
            )
            raise SystemExit(1)
        client = Groq(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as exc:
            print_actionable_error(
                "Groq request failed.",
                "The workflow sent a prompt to Groq, but the API request did not complete successfully.",
                [
                    "Check your internet connection and GROQ_API_KEY.",
                    "Check whether the selected model is available.",
                    f"Original error: {exc}",
                ],
            )
            raise SystemExit(1) from exc
        return response.choices[0].message.content or ""

    try:
        response = ollama_chat(
            model=model,
            messages=messages,
            options={"temperature": 0.2},
        )
    except Exception as exc:
        print_actionable_error(
            "Ollama request failed.",
            "This workflow uses a local Ollama model, so the server and model must be available before the graph can continue.",
            [
                "Run ollama serve in another terminal.",
                f"Pull the model with: ollama pull {model}",
                f"Original error: {exc}",
            ],
        )
        raise SystemExit(1) from exc
    return response["message"]["content"]


def _call_structured(
    *,
    messages: list[dict[str, str]],
    provider: str,
    model: str,
    schema_dict: dict[str, Any],
) -> str:
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            print_actionable_error(
                "GROQ_API_KEY was not found.",
                "This workflow is asking Groq for structured JSON output.",
                [
                    "Create a .env file in the project root.",
                    "Add GROQ_API_KEY=your_key_here.",
                    "Re-run with --provider groq, or use --provider ollama.",
                ],
            )
            raise SystemExit(1)
        client = Groq(api_key=api_key)
        schema_instruction = {
            "role": "system",
            "content": (
                "Return only valid JSON. The output must match this JSON Schema exactly:\n"
                f"{json.dumps(schema_dict)}"
            ),
        }
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[schema_instruction, *messages],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "{}"
        except BadRequestError as exc:
            # Groq can reject the request when server-side JSON validation fails,
            # but still include a near-JSON candidate in `failed_generation`.
            # Return that text so our existing parse/validate/retry loop can repair it.
            payload = getattr(exc, "body", None)
            if isinstance(payload, dict):
                error_obj = payload.get("error")
                if isinstance(error_obj, dict):
                    failed_generation = error_obj.get("failed_generation")
                    if isinstance(failed_generation, str) and failed_generation.strip():
                        return failed_generation
            print_actionable_error(
                "Groq structured-output request failed.",
                "The model call failed before Python could validate the JSON result.",
                [
                    "Check your internet connection and GROQ_API_KEY.",
                    "If the model rejected strict JSON, try a different GROQ_MODEL.",
                    f"Original error: {exc}",
                ],
            )
            raise SystemExit(1) from exc

    try:
        response = ollama_chat(
            model=model,
            messages=messages,
            format=schema_dict,
            options={"temperature": 0},
        )
    except Exception as exc:
        print_actionable_error(
            "Ollama structured-output request failed.",
            "The workflow needs a local structured JSON response before it can validate and route state.",
            [
                "Run ollama serve in another terminal.",
                f"Pull the model with: ollama pull {model}",
                f"Original error: {exc}",
            ],
        )
        raise SystemExit(1) from exc
    return response["message"]["content"]


def ask_ollama_text(
    user_prompt: str,
    system_prompt: str = "You are a precise teaching assistant.",
    model: str = DEFAULT_MODEL,
    provider: str | None = None,
) -> str:
    """Legacy helper name kept for compatibility; now supports Ollama or Groq."""
    selected_provider = _resolve_provider(provider)
    selected_model = _resolve_model_for_provider(selected_provider, model)
    return _call_text(
        provider=selected_provider,
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )


def ask_ollama_structured(
    user_prompt: str,
    schema_model: Type[T],
    system_prompt: str = "You are a precise teaching assistant that returns valid JSON only.",
    model: str = DEFAULT_MODEL,
    provider: str | None = None,
    max_retries: int = 2,
) -> T:
    """
    Call Ollama with a JSON schema, validate with Pydantic,
    and retry once or twice if validation fails.

    This helper intentionally shows students a robust local pattern:
    1. ask for structured output
    2. validate
    3. retry with the error message if needed

    In later module examples, this validated output is passed into
    external tool workflows (for example, writing structured content
    into Notion through MCP).
    """
    schema_dict = schema_model.model_json_schema()
    selected_provider = _resolve_provider(provider)
    selected_model = _resolve_model_for_provider(selected_provider, model)
    prompt = textwrap.dedent(
        f"""
        Return output that matches this JSON schema exactly.

        JSON schema:
        {json.dumps(schema_dict, indent=2)}

        Task:
        {user_prompt}
        """
    ).strip()

    last_error: Exception | None = None

    for attempt in range(1, max_retries + 2):
        raw_text = _call_structured(
            provider=selected_provider,
            model=selected_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            schema_dict=schema_dict,
        )

        try:
            return schema_model.model_validate_json(raw_text)
        except ValidationError as exc:
            last_error = exc
            try:
                repaired = extract_json_block(raw_text)
                return schema_model.model_validate_json(repaired)
            except Exception as inner_exc:
                last_error = inner_exc
                prompt = textwrap.dedent(
                    f"""
                    Your previous response did not validate.

                    Validation error:
                    {str(exc)}

                    You must now return ONLY valid JSON that matches this schema exactly:
                    {json.dumps(schema_dict, indent=2)}

                    Original task:
                    {user_prompt}
                    """
                ).strip()

    raise RuntimeError(f"Structured output failed after retries. Last error: {last_error}")


def model_or_fallback(
    primary_fn,
    fallback_value,
    fallback_message: str,
):
    """
    Small helper to keep classroom scripts resilient.
    """
    try:
        return primary_fn()
    except Exception as exc:
        print(f"\n[warning] {fallback_message}")
        print(f"[warning] Details: {exc}")
        return fallback_value
