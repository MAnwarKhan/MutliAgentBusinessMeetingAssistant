from __future__ import annotations

import json
from collections.abc import Callable

from pydantic import ValidationError

from .agents import LLMAgent
from .models import ActionItem, AgentOutput, MeetingInput, MeetingResult
from .prompts import ACTIONS_AGENT, CONTEXT_AGENT, DECISIONS_AGENT, REVIEW_AGENT
from .utils import extract_json


class MeetingAssistant:
    """Sequential four-agent workflow with a final quality-review step."""

    def __init__(self, api_key: str, model: str = "gpt-5-mini", client=None):
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
        self.client = client
        self.model = model

        self.context_agent = LLMAgent(
            self.client, "Agent 1 — Context & Requirements", CONTEXT_AGENT, model
        )
        self.decisions_agent = LLMAgent(
            self.client, "Agent 2 — Decisions", DECISIONS_AGENT, model
        )
        self.actions_agent = LLMAgent(
            self.client, "Agent 3 — Action Items", ACTIONS_AGENT, model
        )
        self.review_agent = LLMAgent(
            self.client, "Agent 4 — Executive Brief & Quality Review", REVIEW_AGENT, model
        )

    @staticmethod
    def _meeting_text(meeting: MeetingInput) -> str:
        return (
            f"MEETING TITLE: {meeting.title}\n"
            f"DATE: {meeting.date or 'Not specified'}\n"
            f"PARTICIPANTS: {', '.join(meeting.participants) or 'Not specified'}\n"
            f"OBJECTIVE: {meeting.objective or 'Not specified'}\n\n"
            f"TRANSCRIPT:\n{meeting.transcript}"
        )

    def run(
        self,
        meeting: MeetingInput,
        status_callback: Callable[[str], None] | None = None,
    ) -> MeetingResult:
        notify = status_callback or (lambda _: None)
        base = self._meeting_text(meeting)
        outputs: list[AgentOutput] = []

        notify("Agent 1 is identifying requirements, constraints, and stakeholder needs.")
        context = self.context_agent.run(base)
        outputs.append(AgentOutput(agent_name=self.context_agent.name, content=context))

        notify("Agent 2 is separating confirmed decisions from proposals and open questions.")
        decision_input = f"{base}\n\nAGENT 1 ANALYSIS:\n{context}"
        decisions_text = self.decisions_agent.run(decision_input)
        outputs.append(AgentOutput(agent_name=self.decisions_agent.name, content=decisions_text))

        notify("Agent 3 is extracting owners, deliverables, and deadlines.")
        actions_input = (
            f"{base}\n\nAGENT 1 ANALYSIS:\n{context}\n\n"
            f"AGENT 2 ANALYSIS:\n{decisions_text}"
        )
        actions_text = self.actions_agent.run(actions_input)
        outputs.append(AgentOutput(agent_name=self.actions_agent.name, content=actions_text))
        action_payload = extract_json(actions_text)

        try:
            action_items = [
                ActionItem.model_validate(item)
                for item in action_payload.get("action_items", [])
            ]
        except (ValidationError, TypeError) as exc:
            raise ValueError(f"Agent 3 returned invalid action-item data: {exc}") from exc

        notify("Agent 4 is checking accuracy and producing the executive brief.")
        review_input = (
            f"{base}\n\nAGENT 1 ANALYSIS:\n{context}\n\n"
            f"AGENT 2 ANALYSIS:\n{decisions_text}\n\n"
            f"AGENT 3 JSON:\n{json.dumps(action_payload, indent=2)}"
        )
        review_text = self.review_agent.run(review_input)
        outputs.append(AgentOutput(agent_name=self.review_agent.name, content=review_text))
        review = extract_json(review_text)

        return MeetingResult(
            executive_brief=str(review.get("executive_brief", "")).strip(),
            decisions=[str(x) for x in review.get("decisions", [])],
            action_items=action_items,
            risks_and_open_questions=[
                str(x) for x in review.get("risks_and_open_questions", [])
            ],
            agent_outputs=outputs,
        )
