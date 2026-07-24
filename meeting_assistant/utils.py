from __future__ import annotations

import json
import os
import re
from typing import Any


def get_api_key(streamlit_module=None) -> str | None:
    """Read the key safely from Streamlit Secrets, then the environment."""
    if streamlit_module is not None:
        try:
            value = streamlit_module.secrets.get("OPENAI_API_KEY")
            if value:
                return str(value)
        except Exception:
            pass
    return os.getenv("OPENAI_API_KEY")


def extract_json(text: str) -> dict[str, Any]:
    """Parse a JSON object, tolerating Markdown code fences around it."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("The model did not return a JSON object.")
        value = json.loads(cleaned[start : end + 1])

    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object from the model.")
    return value
