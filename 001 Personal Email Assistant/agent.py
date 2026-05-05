from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from gmail_tool import fetch_emails


@tool
def read_inbox(max_results: int = 10, query: str = "") -> str:
    """Fetch emails from the Gmail inbox. Optionally filter with a Gmail search query."""
    emails = fetch_emails(max_results=max_results, query=query)
    if not emails:
        return "No emails found."

    lines = []
    for i, e in enumerate(emails, 1):
        lines.append(
            f"[{i}] From: {e['from']}\n"
            f"    Date: {e['date']}\n"
            f"    Subject: {e['subject']}\n"
            f"    Preview: {e['body'][:200]}\n"
        )
    return "\n".join(lines)


@tool
def classify_emails(max_results: int = 10) -> str:
    """Classify the most recent emails into categories: Work, Personal, Newsletter, Urgent, or Spam."""
    emails = fetch_emails(max_results=max_results)
    if not emails:
        return "No emails to classify."

    results = []
    for e in emails:
        subject = e["subject"].lower()
        sender = e["from"].lower()
        body = e["body"].lower()

        if any(k in subject + body for k in ["unsubscribe", "newsletter", "digest", "weekly"]):
            category = "Newsletter"
        elif any(k in subject + body for k in ["urgent", "asap", "immediately", "action required"]):
            category = "Urgent"
        elif any(k in sender for k in ["noreply", "no-reply", "mailer", "notification", "donotreply"]):
            category = "Spam / Automated"
        elif any(k in subject + body + sender for k in ["meeting", "deadline", "project", "invoice", "client", "work"]):
            category = "Work"
        else:
            category = "Personal"

        results.append(f"• [{category}] {e['subject']} — from {e['from']}")

    return "\n".join(results)


@tool
def draft_reply(subject: str, sender: str, original_body: str) -> str:
    """
    Draft a professional reply for an email.
    Provide the subject, sender name/address, and the original email body.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    prompt = (
        "You are a professional email assistant. Draft a concise, polite reply "
        "to the following email.\n\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Body:\n{original_body}\n\n"
        "Write only the reply body — no subject line, no headers."
    )
    response = llm.invoke(prompt)
    return response.content


@tool
def extract_action_items(max_results: int = 10) -> str:
    """Read the inbox and return a bullet-point list of action items found across all emails."""
    emails = fetch_emails(max_results=max_results)
    if not emails:
        return "No emails found."

    combined = "\n".join(
        f"Subject: {e['subject']}\nBody: {e['body']}" for e in emails
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = (
        "You are an assistant that extracts action items from emails. "
        "Read the following emails and return ONLY a bullet-point list of tasks "
        "or actions that require follow-up. Be concise.\n\n"
        + combined
    )
    response = llm.invoke(prompt)
    return response.content


_TOOLS = [read_inbox, classify_emails, draft_reply, extract_action_items]

_SYSTEM_PROMPT = (
    "You are a helpful personal email assistant with access to the user's Gmail inbox. "
    "Use the available tools to read, classify, summarize, and act on emails. "
    "Be concise and professional."
)


def run_agent(user_input: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_react_agent(llm, _TOOLS, prompt=_SYSTEM_PROMPT)
    result = agent.invoke({"messages": [("human", user_input)]})
    return result["messages"][-1].content
