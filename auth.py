import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(PROJECT_DIR, "token.pickle")
CREDENTIALS_FILE = os.path.join(PROJECT_DIR, "credentials.json")


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found. Download it from the Google Cloud Console "
                    "(APIs & Services > Credentials > OAuth 2.0 Client IDs > Download JSON)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds


def build_services():
    creds = get_credentials()
    calendar = build("calendar", "v3", credentials=creds)
    gmail = build("gmail", "v1", credentials=creds)
    return calendar, gmail
