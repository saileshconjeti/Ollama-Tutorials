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

from ollama import chat
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:0.5b")


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


def ask_ollama_text(
    user_prompt: str,
    system_prompt: str = "You are a precise teaching assistant.",
    model: str = DEFAULT_MODEL,
) -> str:
    response = chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]


def ask_ollama_structured(
    user_prompt: str,
    schema_model: Type[T],
    system_prompt: str = "You are a precise teaching assistant that returns valid JSON only.",
    model: str = DEFAULT_MODEL,
    max_retries: int = 2,
) -> T:
    schema_dict = schema_model.model_json_schema()
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

    for _ in range(max_retries + 1):
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            format=schema_dict,
        )

        raw_text = response["message"]["content"]

        try:
            return schema_model.model_validate_json(raw_text)
        except ValidationError as exc:
            last_error = exc
            try:
                repaired = extract_json_block(raw_text)
                return schema_model.model_validate_json(repaired)
            except Exception as inner_exc:
                last_error = inner_exc

    raise RuntimeError(f"Structured output failed after retries. Last error: {last_error}")
