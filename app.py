import streamlit as st

from meeting_assistant.models import MeetingInput
from meeting_assistant.orchestrator import MeetingAssistant
from meeting_assistant.utils import get_api_key

st.set_page_config(
    page_title="AI Business Meeting Assistant",
    page_icon="🤝",
    layout="wide",
)

st.title("🤝 AI Business Meeting Assistant")
st.caption("A simple four-agent system that converts a meeting transcript into business-ready outputs.")

with st.sidebar:
    st.header("Configuration")
    model = st.text_input("OpenAI model", value="gpt-5-mini")
    show_agent_outputs = st.checkbox("Show each agent's output", value=True)
    st.markdown(
        """
        **Agents**
        1. Context & Requirements Analyst  
        2. Decisions Analyst  
        3. Action-Items Manager  
        4. Executive Brief & Quality Reviewer
        """
    )
    st.info("Your API key is read from Streamlit Secrets or the OPENAI_API_KEY environment variable.")

col1, col2 = st.columns(2)
with col1:
    meeting_title = st.text_input("Meeting title", "Weekly Product Planning")
    meeting_date = st.text_input("Meeting date", "2026-07-23")
with col2:
    participants = st.text_input(
        "Participants (comma-separated)",
        "Ayesha, Bilal, Carlos, Dana",
    )
    objective = st.text_input(
        "Meeting objective",
        "Agree on the MVP scope and next steps.",
    )

sample_transcript = """Ayesha: Our goal is to launch the customer support MVP by September 15.
Bilal: The first release should support email tickets and website chat. Voice can wait.
Carlos: The CRM integration may take three weeks. I need API credentials from Dana by Friday.
Dana: I can provide sandbox credentials by July 25. Production access requires a security review.
Ayesha: Decision: email and web chat are in the MVP; voice is postponed to phase two.
Bilal: I will prepare the revised user stories by July 28.
Carlos: I will complete the CRM integration estimate by July 29.
Dana: Security review normally takes ten business days.
Ayesha: Main risk is that production CRM access could delay the September launch.
Bilal: We should meet again next Wednesday to review the estimate and user stories."""

transcript = st.text_area(
    "Meeting transcript",
    value=sample_transcript,
    height=330,
    help="Paste a transcript or structured meeting notes. Do not include confidential information unless approved.",
)

run = st.button("Run Four-Agent Analysis", type="primary", use_container_width=True)

if run:
    api_key = get_api_key(st)
    if not api_key:
        st.error(
            "OpenAI API key not found. Add OPENAI_API_KEY to Streamlit Secrets "
            "or set it as an environment variable."
        )
        st.stop()

    if not transcript.strip():
        st.warning("Please enter a meeting transcript.")
        st.stop()

    meeting = MeetingInput(
        title=meeting_title.strip(),
        date=meeting_date.strip(),
        participants=[p.strip() for p in participants.split(",") if p.strip()],
        objective=objective.strip(),
        transcript=transcript.strip(),
    )

    assistant = MeetingAssistant(api_key=api_key, model=model.strip() or "gpt-5-mini")

    try:
        with st.status("Agents are analyzing the meeting...", expanded=True) as status:
            result = assistant.run(meeting, status_callback=st.write)
            status.update(label="Analysis complete", state="complete", expanded=False)
    except Exception as exc:
        st.exception(exc)
        st.stop()

    st.success("The four-agent analysis is complete.")

    st.subheader("Executive Meeting Brief")
    st.markdown(result.executive_brief)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Confirmed Decisions")
        if result.decisions:
            for item in result.decisions:
                st.markdown(f"- {item}")
        else:
            st.write("No confirmed decisions detected.")

    with c2:
        st.subheader("Risks and Open Questions")
        for item in result.risks_and_open_questions:
            st.markdown(f"- {item}")

    st.subheader("Action Items")
    if result.action_items:
        st.dataframe(
            [item.model_dump() for item in result.action_items],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.write("No action items detected.")

    if show_agent_outputs:
        st.divider()
        st.subheader("Agent Workbench")
        for output in result.agent_outputs:
            with st.expander(output.agent_name):
                st.markdown(output.content)

    st.download_button(
        "Download Meeting Brief (.md)",
        data=result.to_markdown(),
        file_name="meeting_brief.md",
        mime="text/markdown",
        use_container_width=True,
    )
