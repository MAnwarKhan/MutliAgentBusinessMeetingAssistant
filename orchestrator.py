from concurrent.futures import ThreadPoolExecutor


def run(
    self,
    meeting: MeetingInput,
    status_callback=None,
) -> MeetingResult:

    notify = status_callback or (lambda _: None)
    base = self._meeting_text(meeting)
    outputs = []

    notify("Agents 1, 2, and 3 are analyzing the meeting in parallel.")

    with ThreadPoolExecutor(max_workers=3) as executor:
        context_future = executor.submit(
            self.context_agent.run,
            base,
        )

        decisions_future = executor.submit(
            self.decisions_agent.run,
            base,
        )

        actions_future = executor.submit(
            self.actions_agent.run,
            base,
        )

        context = context_future.result()
        decisions_text = decisions_future.result()
        actions_text = actions_future.result()

    outputs.append(
        AgentOutput(
            agent_name=self.context_agent.name,
            content=context,
        )
    )

    outputs.append(
        AgentOutput(
            agent_name=self.decisions_agent.name,
            content=decisions_text,
        )
    )

    outputs.append(
        AgentOutput(
            agent_name=self.actions_agent.name,
            content=actions_text,
        )
    )

    action_payload = extract_json(actions_text)

    action_items = [
        ActionItem.model_validate(item)
        for item in action_payload.get("action_items", [])
    ]

    notify("Agent 4 is verifying the results and preparing the executive brief.")

    review_input = (
        f"{base}\n\n"
        f"AGENT 1 ANALYSIS:\n{context}\n\n"
        f"AGENT 2 ANALYSIS:\n{decisions_text}\n\n"
        f"AGENT 3 JSON:\n{json.dumps(action_payload, indent=2)}"
    )

    review_text = self.review_agent.run(review_input)
    outputs.append(
        AgentOutput(
            agent_name=self.review_agent.name,
            content=review_text,
        )
    )

    review = extract_json(review_text)

    return MeetingResult(
        executive_brief=str(
            review.get("executive_brief", "")
        ).strip(),
        decisions=[
            str(item)
            for item in review.get("decisions", [])
        ],
        action_items=action_items,
        risks_and_open_questions=[
            str(item)
            for item in review.get(
                "risks_and_open_questions",
                [],
            )
        ],
        agent_outputs=outputs,
    )
