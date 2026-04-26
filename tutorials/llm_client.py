import argparse
import json
import os

import ollama
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
# Alternative: "llama-3.3-70b-versatile" for better quality, lower free-tier volume.


def chat(messages, temperature=0.2, provider=None):
    selected_provider, _ = get_selected_provider_and_model(provider)

    if selected_provider == "groq":
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        options={"temperature": temperature},
    )
    return response["message"]["content"]


def stream_chat(messages, temperature=0.2, provider=None):
    selected_provider, _ = get_selected_provider_and_model(provider)

    if selected_provider == "groq":
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content
        return

    stream = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        options={"temperature": temperature},
        stream=True,
    )
    for chunk in stream:
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield content


def structured_chat(messages, schema, temperature=0.0, provider=None):
    selected_provider, _ = get_selected_provider_and_model(provider)

    if selected_provider == "groq":
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        schema_instruction = {
            "role": "system",
            "content": (
                "Return only valid JSON. The output must match this JSON Schema exactly:\n"
                f"{json.dumps(schema)}"
            ),
        }
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[schema_instruction, *messages],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        format=schema,
        options={"temperature": temperature},
    )
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
