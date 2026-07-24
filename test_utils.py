import pytest

from meeting_assistant.utils import extract_json


def test_extract_json_plain():
    assert extract_json('{"value": 7}') == {"value": 7}


def test_extract_json_fenced():
    assert extract_json('```json\n{"value": 7}\n```') == {"value": 7}


def test_extract_json_with_extra_text():
    assert extract_json('Result:\n{"value": 7}\nDone') == {"value": 7}


def test_extract_json_rejects_non_json():
    with pytest.raises(ValueError):
        extract_json("No JSON here")
