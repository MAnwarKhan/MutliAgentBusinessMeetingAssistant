from types import SimpleNamespace

from meeting_assistant.models import MeetingInput
from meeting_assistant.orchestrator import MeetingAssistant


class FakeResponses:
    def __init__(self):
        self.index = 0
        self.outputs = [
            "## Purpose\nPlan the MVP.\n## Constraint\nCRM access.",
            "## Confirmed\nEmail and chat are approved.",
            """{"action_items":[{"task":"Provide sandbox credentials","owner":"Dana","due_date":"July 25","status":"Open","evidence":"I can provide sandbox credentials by July 25."}]}""",
            """{"executive_brief":"The team confirmed the MVP scope and assigned the CRM credential task.","decisions":["Email and web chat are in the MVP; voice is deferred."],"risks_and_open_questions":["Production CRM access may delay launch."]}""",
        ]

    def create(self, **kwargs):
        output = self.outputs[self.index]
        self.index += 1
        return SimpleNamespace(output_text=output)


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_four_agent_workflow():
    assistant = MeetingAssistant(api_key="test", client=FakeClient())
    meeting = MeetingInput(
        title="MVP Planning",
        transcript="Dana will provide sandbox credentials by July 25.",
    )
    result = assistant.run(meeting)

    assert len(result.agent_outputs) == 4
    assert len(result.action_items) == 1
    assert result.action_items[0].owner == "Dana"
    assert result.decisions
    assert result.risks_and_open_questions
