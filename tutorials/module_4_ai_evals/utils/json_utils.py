import json
import re

from tutorials.terminal_utils import print_actionable_error


def extract_json(text: str) -> dict:
    """Parse a JSON object from model output, even if extra text is included."""
    # Best case: the model followed instructions and returned pure JSON.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Common classroom-demo case: the model writes prose before or after the JSON.
    # This regex extracts the first JSON-looking object from the full response.
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # If both parsing attempts fail, show the raw output so students can debug it.
    print_actionable_error(
        "Could not parse JSON from the judge response.",
        "The next step expects rubric scores as structured data, but the model output was not valid JSON.",
        [
            "Read the raw judge response printed above.",
            "Check whether the prompt still asks for JSON.",
            "Re-run once; model formatting errors can be transient.",
        ],
    )
    raise ValueError(f"Could not parse JSON from model output:\n{text}")
