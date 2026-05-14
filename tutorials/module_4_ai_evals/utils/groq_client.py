import os

from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, Groq

from tutorials.terminal_utils import print_actionable_error


# Load variables from a local .env file so students do not hardcode secrets.
load_dotenv()

# This is a small, fast Groq-hosted model. Students can override it in .env.
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


def get_selected_groq_model(model: str | None = None) -> str:
    """Return the Groq model that will be used for a call."""
    return model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)


def call_groq_llm(
    prompt: str,
    temperature: float = 0.0,
    model: str | None = None,
) -> str:
    """Send one prompt to a Groq-hosted chat model and return the text reply."""
    # GROQ_API_KEY should be stored in .env, never directly in source code.
    api_key = os.getenv("GROQ_API_KEY")

    # Most scripts use the .env model. Tutorial 04 passes model=... to compare judges.
    selected_model = get_selected_groq_model(model)

    # Fail early with an actionable classroom-friendly message.
    if not api_key or api_key == "your_groq_api_key_here":
        print_actionable_error(
            "GROQ_API_KEY was not found.",
            "Module 4 uses Groq-hosted judge models so students can run the same evaluation prompt consistently.",
            [
                "Create tutorials/module_4_ai_evals/.env from .env.example, or create a project-root .env.",
                "Add GROQ_API_KEY=your_key_here.",
                "Re-run the script from the module_4_ai_evals folder.",
            ],
        )
        raise SystemExit(1)

    # The official Groq SDK handles the HTTPS request and response object.
    client = Groq(api_key=api_key)

    # temperature=0.0 makes the judge more consistent across repeated runs.
    try:
        response = client.chat.completions.create(
            model=selected_model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        # The system message defines the model's role before the task prompt.
                        "You are a careful evaluator. Follow the requested output "
                        "format exactly."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
    except (APIConnectionError, APIStatusError) as exc:
        print_actionable_error(
            "Groq judge request failed.",
            "The evaluation prompt was ready, but the cloud model did not return a usable response.",
            [
                "Check your internet connection and GROQ_API_KEY.",
                "Check whether the selected GROQ_MODEL is available.",
                "If the API is rate limited, wait briefly and re-run the script.",
                f"Details from the SDK: {exc}",
            ],
        )
        raise SystemExit(1) from exc

    # Groq returns a list of choices. For these demos, we only request one answer.
    return response.choices[0].message.content
