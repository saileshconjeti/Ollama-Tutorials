# File name: agent_utils.py
# Purpose: Shared helpers for Module 3 AI agent tutorials.
# Concepts covered: structured output, retry validation, terminal formatting.
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

from __future__ import annotations

import json
import os
import re
import textwrap
from typing import Any, Type, TypeVar

from dotenv import load_dotenv
from groq import BadRequestError, Groq
from ollama import chat as ollama_chat
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

load_dotenv()

DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
DEFAULT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:0.5b")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def print_header(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def print_subheader(title: str) -> None:
    print("\n" + "-" * 90)
    print(title)
    print("-" * 90)


def pretty_json(data: Any) -> str:
    # Support nested Pydantic models inside dict/list structures.
    def _default_serializer(obj: Any):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    if isinstance(data, BaseModel):
        return json.dumps(data.model_dump(), indent=2)
    return json.dumps(data, indent=2, default=_default_serializer)


def extract_json_block(text: str) -> str:
    text = text.strip()
    if text.startswith("{") or text.startswith("["):
        return text

    match = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
    if match:
        return match.group(1)

    raise ValueError("Could not find a JSON block in model output.")


def _looks_like_ollama_model(model: str) -> bool:
    return ":" in model


def _resolve_provider(provider: str | None) -> str:
    selected = (provider or DEFAULT_PROVIDER).lower()
    if selected not in {"ollama", "groq"}:
        return "ollama"
    return selected


def _resolve_model_for_provider(provider: str, model: str) -> str:
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
            raise RuntimeError("Missing GROQ_API_KEY for Groq provider.")
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    response = ollama_chat(
        model=model,
        messages=messages,
        options={"temperature": 0.2},
    )
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
            raise RuntimeError("Missing GROQ_API_KEY for Groq provider.")
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
            payload = getattr(exc, "body", None)
            if isinstance(payload, dict):
                error_obj = payload.get("error")
                if isinstance(error_obj, dict):
                    failed_generation = error_obj.get("failed_generation")
                    if isinstance(failed_generation, str) and failed_generation.strip():
                        return failed_generation
            raise

    response = ollama_chat(
        model=model,
        messages=messages,
        format=schema_dict,
        options={"temperature": 0},
    )
    return response["message"]["content"]


def ask_ollama_text(
    user_prompt: str,
    system_prompt: str = "You are a precise teaching assistant.",
    model: str = DEFAULT_MODEL,
    provider: str | None = None,
) -> str:
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

    for _attempt in range(1, max_retries + 2):
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
