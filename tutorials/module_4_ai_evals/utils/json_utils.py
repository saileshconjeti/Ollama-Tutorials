import json
import re


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
    raise ValueError(f"Could not parse JSON from model output:\n{text}")
