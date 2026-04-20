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
import textwrap
from typing import Any, Type, TypeVar

from ollama import chat
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen3:4b")


def print_header(title: str) -> None:
    """Print a simple section header for terminal demos."""
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def print_subheader(title: str) -> None:
    """Print a smaller section header."""
    print("\n" + "-" * 90)
    print(title)
    print("-" * 90)


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


def ask_ollama_text(
    user_prompt: str,
    system_prompt: str = "You are a precise teaching assistant.",
    model: str = DEFAULT_MODEL,
) -> str:
    """Call Ollama for a normal text response."""
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
