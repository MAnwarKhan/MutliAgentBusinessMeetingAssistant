from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class MeetingInput(BaseModel):
    title: str = Field(min_length=1)
    date: str = ""
    participants: List[str] = Field(default_factory=list)
    objective: str = ""
    transcript: str = Field(min_length=1)


class ActionItem(BaseModel):
    task: str
    owner: str = "Unassigned"
    due_date: str = "Not specified"
    status: str = "Open"
    evidence: str = ""


class AgentOutput(BaseModel):
    agent_name: str
    content: str


class MeetingResult(BaseModel):
    executive_brief: str
    decisions: List[str] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    risks_and_open_questions: List[str] = Field(default_factory=list)
    agent_outputs: List[AgentOutput] = Field(default_factory=list)

    def to_markdown(self) -> str:
        decisions = "\n".join(f"- {x}" for x in self.decisions) or "- None identified"
        risks = "\n".join(f"- {x}" for x in self.risks_and_open_questions) or "- None identified"
        actions = "\n".join(
            f"- **{a.task}** — Owner: {a.owner}; Due: {a.due_date}; Status: {a.status}"
            for a in self.action_items
        ) or "- None identified"

        return (
            "# Executive Meeting Brief\n\n"
            f"{self.executive_brief}\n\n"
            "## Confirmed Decisions\n\n"
            f"{decisions}\n\n"
            "## Action Items\n\n"
            f"{actions}\n\n"
            "## Risks and Open Questions\n\n"
            f"{risks}\n"
        )
