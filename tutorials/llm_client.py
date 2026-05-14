import argparse
import json
import os

import ollama
from groq import APIConnectionError, APIStatusError
from dotenv import load_dotenv
from groq import Groq

from tutorials.terminal_utils import print_actionable_error

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
# Alternative: "llama-3.3-70b-versatile" for better quality, lower free-tier volume.


def chat(messages, temperature=0.2, provider=None):
    selected_provider, _ = get_selected_provider_and_model(provider)

    if selected_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            print_actionable_error(
                "GROQ_API_KEY was not found.",
                "This tutorial uses Groq as the cloud LLM provider when --provider groq is selected.",
                [
                    "Create a .env file in the project root.",
                    "Add GROQ_API_KEY=your_key_here.",
                    "Re-run the script, or use --provider ollama for a local run.",
                ],
            )
            raise SystemExit(1)
        client = Groq(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=temperature,
            )
        except (APIConnectionError, APIStatusError) as exc:
            print_actionable_error(
                "Groq request failed.",
                "The script sent a prompt to Groq, but the API did not return a usable response.",
                [
                    "Check your internet connection and GROQ_API_KEY.",
                    "Check whether the selected GROQ_MODEL is available for your account.",
                    f"Details from the SDK: {exc}",
                ],
            )
            raise SystemExit(1) from exc
        return response.choices[0].message.content

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": temperature},
        )
    except Exception as exc:
        print_actionable_error(
            "Ollama chat request failed.",
            "This tutorial uses a local Ollama model. The Python call cannot continue unless Ollama is running and the model is available.",
            [
                "Run ollama serve in another terminal.",
                f"Pull the model with: ollama pull {OLLAMA_MODEL}",
                f"Original error: {exc}",
            ],
        )
        raise SystemExit(1) from exc
    return response["message"]["content"]


def stream_chat(messages, temperature=0.2, provider=None):
    selected_provider, _ = get_selected_provider_and_model(provider)

    if selected_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            print_actionable_error(
                "GROQ_API_KEY was not found.",
                "Streaming with Groq needs a cloud API key before the request can be sent.",
                [
                    "Create a .env file in the project root.",
                    "Add GROQ_API_KEY=your_key_here.",
                    "Re-run the script, or use --provider ollama.",
                ],
            )
            raise SystemExit(1)
        client = Groq(api_key=api_key)
        try:
            stream = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
        except (APIConnectionError, APIStatusError) as exc:
            print_actionable_error(
                "Groq streaming request failed.",
                "The tutorial could not open a streaming response from Groq.",
                [
                    "Check your internet connection and GROQ_API_KEY.",
                    "Try again in a moment if the API is rate limited.",
                    f"Details from the SDK: {exc}",
                ],
            )
            raise SystemExit(1) from exc
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content
        return

    try:
        stream = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": temperature},
            stream=True,
        )
    except Exception as exc:
        print_actionable_error(
            "Ollama streaming request failed.",
            "Streaming needs the local Ollama server and the selected model before tokens can appear in the terminal.",
            [
                "Run ollama serve in another terminal.",
                f"Pull the model with: ollama pull {OLLAMA_MODEL}",
                f"Original error: {exc}",
            ],
        )
        raise SystemExit(1) from exc
    for chunk in stream:
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield content


def structured_chat(messages, schema, temperature=0.0, provider=None):
    selected_provider, _ = get_selected_provider_and_model(provider)

    if selected_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            print_actionable_error(
                "GROQ_API_KEY was not found.",
                "Structured output with Groq requires an API key before the model can produce JSON.",
                [
                    "Create a .env file in the project root.",
                    "Add GROQ_API_KEY=your_key_here.",
                    "Re-run the script, or use --provider ollama.",
                ],
            )
            raise SystemExit(1)
        client = Groq(api_key=api_key)
        schema_instruction = {
            "role": "system",
            "content": (
                "Return only valid JSON. The output must match this JSON Schema exactly:\n"
                f"{json.dumps(schema)}"
            ),
        }
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[schema_instruction, *messages],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
        except (APIConnectionError, APIStatusError) as exc:
            print_actionable_error(
                "Groq structured-output request failed.",
                "The script asked Groq for JSON, but the API request did not complete successfully.",
                [
                    "Check your internet connection and GROQ_API_KEY.",
                    "If rate limited, wait briefly and re-run the script.",
                    f"Details from the SDK: {exc}",
                ],
            )
            raise SystemExit(1) from exc
        return response.choices[0].message.content

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            format=schema,
            options={"temperature": temperature},
        )
    except Exception as exc:
        print_actionable_error(
            "Ollama structured-output request failed.",
            "The local model did not return a structured response because the Ollama call failed.",
            [
                "Run ollama serve in another terminal.",
                f"Pull the model with: ollama pull {OLLAMA_MODEL}",
                f"Original error: {exc}",
            ],
        )
        raise SystemExit(1) from exc
    return response["message"]["content"]


def get_selected_provider_and_model(provider=None):
    selected_provider = (provider or PROVIDER).lower()
    selected_model = GROQ_MODEL if selected_provider == "groq" else OLLAMA_MODEL
    return selected_provider, selected_model


def build_provider_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--provider",
        choices=["ollama", "groq"],
        default=None,
        help="Override LLM provider for this run. If omitted, uses LLM_PROVIDER from .env.",
    )
    return parser


def parse_provider_from_cli(description):
    parser = build_provider_parser(description)
    args = parser.parse_args()
    return args.provider
