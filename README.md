# AI Business Meeting Assistant

A beginner-friendly multi-agent AI application built with Python, OpenAI, and Streamlit.

## What the four agents do

1. **Context & Requirements Analyst** identifies the meeting objective, requirements, constraints, dependencies, assumptions, and stakeholder concerns.
2. **Decisions Analyst** separates confirmed decisions from proposals, deferred items, risks, and unresolved questions.
3. **Action-Items Manager** extracts tasks, owners, deadlines, status, and supporting transcript evidence.
4. **Executive Brief & Quality Reviewer** checks earlier outputs against the transcript and produces the final business-ready brief.

The agents run sequentially. Each agent receives the original meeting information, while later agents also receive relevant outputs from earlier agents. The fourth agent serves as a quality-control layer.

## Architecture

```text
Meeting transcript
       |
       v
Agent 1: Context & Requirements
       |
       v
Agent 2: Decisions
       |
       v
Agent 3: Action Items (JSON)
       |
       v
Agent 4: Executive Brief + Quality Review (JSON)
       |
       v
Streamlit dashboard + Markdown download
```

## Repository structure

```text
ai-business-meeting-assistant/
├── app.py
├── meeting_assistant/
│   ├── __init__.py
│   ├── agents.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── prompts.py
│   └── utils.py
├── tests/
│   ├── test_orchestrator.py
│   └── test_utils.py
├── .streamlit/
│   └── secrets.toml.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Run locally

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Create `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

Run the tests:

```bash
pytest -q
```

Start the application:

```bash
streamlit run app.py
```

## Upload to GitHub

1. Create a new empty GitHub repository.
2. Upload every file and folder from this project.
3. Confirm that `.streamlit/secrets.toml` is **not** uploaded.
4. The example secrets file is safe because it contains no real key.

## Deploy to Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud using GitHub.
2. Select **Create app**.
3. Choose your repository, branch, and `app.py` as the entrypoint.
4. Open the app's **Secrets** settings and add:

```toml
OPENAI_API_KEY = "sk-your-real-key"
```

5. Deploy the app.

## Important security note

Never paste an OpenAI API key directly into source code or commit it to GitHub. Meeting transcripts can contain sensitive business information, so use only data you are authorized to process.

## Current scope and deliberate limitations

This first version uses pasted transcripts. It does not record audio, identify speakers from audio, join video calls, store meetings, send email, or write tasks to external project-management systems. Those can be added later without changing the basic four-agent design.
