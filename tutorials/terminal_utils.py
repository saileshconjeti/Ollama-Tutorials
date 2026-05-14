"""Small plain-text helpers for classroom terminal demos.

These utilities intentionally use only the Python standard library so the
tutorial scripts behave the same in macOS Terminal, Windows PowerShell, Linux,
and VS Code's integrated terminal.
"""

from __future__ import annotations

import json
import os
import textwrap
import time
from typing import Any, Iterable


LINE_WIDTH = 60


def print_separator(width: int = LINE_WIDTH, char: str = "=") -> None:
    print(char * width)


def print_header(title: str) -> None:
    print()
    print_separator()
    print(f"TUTORIAL: {title}")
    print_separator()


def print_step(number: int, title: str) -> None:
    print()
    print(f"STEP {number}: {title}")
    print("-" * LINE_WIDTH)


def print_substep(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def print_ascii_tree(text: str) -> None:
    print(textwrap.dedent(text).strip("\n"))


def print_kv(label: str, value: Any) -> None:
    print(f"{label}: {value}")


def truncate_text(text: str, max_chars: int = 700) -> str:
    normalized = textwrap.dedent(str(text)).strip()
    if len(normalized) <= max_chars:
        return normalized
    omitted = len(normalized) - max_chars
    return normalized[:max_chars].rstrip() + f"\n... [truncated {omitted} characters]"


def print_text_preview(label: str, text: str, max_chars: int = 700) -> None:
    print(f"{label} preview ({min(len(text), max_chars)} of {len(text)} chars):")
    print(truncate_text(text, max_chars=max_chars))


def print_prompt_preview(prompt: str, max_chars: int = 700) -> None:
    print_text_preview("Prompt", prompt, max_chars=max_chars)


def print_json(data: Any) -> None:
    def _default(obj: Any) -> Any:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    print(json.dumps(data, indent=2, default=_default))


def stream_text(text_or_generator: str | Iterable[str], delay: float = 0.0) -> str:
    """Print text progressively and return the full accumulated string."""
    collected: list[str] = []

    if isinstance(text_or_generator, str):
        iterable: Iterable[str] = text_or_generator
    else:
        iterable = text_or_generator

    for chunk in iterable:
        print(chunk, end="", flush=True)
        collected.append(chunk)
        if delay:
            time.sleep(delay)
    print()
    return "".join(collected)


def mask_secret(value: str | None, visible: int = 4) -> str:
    if not value:
        return "[not set]"
    if len(value) <= visible:
        return "*" * len(value)
    return f"{value[:3]}...{value[-visible:]}"


def print_masked_env(name: str) -> None:
    print_kv(name, mask_secret(os.getenv(name)))


def print_actionable_error(title: str, why: str, fixes: list[str]) -> None:
    print()
    print(f"ERROR: {title}")
    print("Why this matters:")
    print(textwrap.fill(why, width=76))
    print()
    print("Fix:")
    for index, fix in enumerate(fixes, start=1):
        print(f"{index}. {fix}")
