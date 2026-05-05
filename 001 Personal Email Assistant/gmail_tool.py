import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_body(payload) -> str:
    """Extract plain-text body from a message payload, handling multipart."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if payload.get("mimeType", "").startswith("multipart"):
        for part in payload.get("parts", []):
            text = get_body(part)
            if text:
                return text

    return ""


def fetch_emails(max_results: int = 10, query: str = "") -> list[dict]:
    """Return a list of email dicts with keys: id, subject, from, date, body."""
    service = get_gmail_service()

    list_kwargs = {"userId": "me", "maxResults": max_results}
    if query:
        list_kwargs["q"] = query

    response = service.users().messages().list(**list_kwargs).execute()
    messages = response.get("messages", [])

    emails = []
    for msg_ref in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_ref["id"], format="full")
            .execute()
        )

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        body = get_body(msg["payload"])

        emails.append(
            {
                "id": msg["id"],
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", "(unknown)"),
                "date": headers.get("Date", "(unknown)"),
                "body": body[:500].strip(),
            }
        )

    return emails
