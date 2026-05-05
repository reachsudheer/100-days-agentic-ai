# Day 001 — Personal Email Assistant

> Part of the **100-day Agentic AI Challenge**

A Streamlit app that connects to your Gmail inbox via the Gmail API and uses a LangChain agent (GPT-4o-mini) to read, classify, extract action items, and draft replies.

---

## Prerequisites

### 1. Get `credentials.json` from Google Cloud Console

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/) and create a new project (or select an existing one).
2. Enable the **Gmail API**: APIs & Services → Library → search "Gmail API" → Enable.
3. Go to **APIs & Services → OAuth consent screen**:
   - Choose **External**.
   - Fill in App name, user support email, and developer email.
   - Add scope: `https://www.googleapis.com/auth/gmail.readonly`.
   - Add your Gmail address as a **Test user**.
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**.
   - Click **Create**, then **Download JSON**.
5. Rename the downloaded file to `credentials.json` and place it in this directory.

### 2. Set your OpenAI API key in `.env`

Open `.env` and replace the placeholder:

```
OPENAI_API_KEY=sk-...your-real-key...
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running the app

```bash
streamlit run app.py
```

On **first run**, a browser window will open asking you to authorize Gmail access. After you approve, a `token.json` file is saved locally — you won't be asked again unless the token expires.

---

## Features

| Button | What it does |
|---|---|
| Read & Classify Inbox | Fetches 10 emails and labels each as Work / Personal / Newsletter / Urgent / Spam |
| Extract Action Items | Reads 10 emails and returns a bullet list of tasks needing follow-up |
| Draft Replies | Drafts professional replies for emails that aren't automated/newsletters |
| Free-text query | Ask anything — the agent decides which tools to call |

---

## Project structure

```
001 Personal Email Assistant/
├── .env                  # OPENAI_API_KEY (never commit this)
├── requirements.txt
├── credentials.json      # Add manually from Google Cloud Console (never commit)
├── token.json            # Created automatically on first OAuth login
├── gmail_tool.py         # Gmail API auth + fetch_emails()
├── agent.py              # LangChain agent + 4 tools (GPT-4o-mini)
└── app.py                # Streamlit UI
```
