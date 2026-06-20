from email.utils import parsedate_to_datetime

LABEL_NAMES = {
    "INBOX": "Inbox",
    "CATEGORY_PROMOTIONS": "Promotions",
    "CATEGORY_SOCIAL": "Social",
    "CATEGORY_UPDATES": "Updates",
}


def get_unread_count(service):
    result = service.users().labels().get(userId="me", id="INBOX").execute()
    return result.get("messagesUnread", 0)


def get_unread_by_label(service):
    counts = {}
    for label_id, label_name in LABEL_NAMES.items():
        try:
            result = service.users().labels().get(userId="me", id=label_id).execute()
            count = result.get("messagesUnread", 0)
            if count > 0:
                counts[label_name] = count
        except Exception:
            pass
    return counts


def get_recent_unread(service, max_results=10):
    result = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=max_results,
    ).execute()

    messages = result.get("messages", [])
    emails = []

    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        date_str = headers.get("Date", "")
        try:
            date = parsedate_to_datetime(date_str)
        except Exception:
            date = None

        emails.append({
            "subject": headers.get("Subject", "(No subject)"),
            "from": headers.get("From", ""),
            "date": date,
            "snippet": detail.get("snippet", ""),
        })

    return emails
