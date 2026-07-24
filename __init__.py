"""AI Business Meeting Assistant package."""

__all__ = ["MeetingAssistant"]


def __getattr__(name):
    if name == "MeetingAssistant":
        from .orchestrator import MeetingAssistant
        return MeetingAssistant
    raise AttributeError(name)
