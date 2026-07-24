from __future__ import annotations

from typing import Any


class LLMAgent:
    def __init__(self, client: Any, name: str, instructions: str, model: str):
        self.client = client
        self.name = name
        self.instructions = instructions
        self.model = model

    def run(self, input_text: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=input_text,
        )
        output = response.output_text.strip()
        if not output:
            raise RuntimeError(f"{self.name} returned an empty response.")
        return output
