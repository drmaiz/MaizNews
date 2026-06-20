from datetime import datetime, timezone, timedelta


def get_events(service, days=7):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)

    result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for item in result.get("items", []):
        start_raw = item["start"].get("dateTime") or item["start"].get("date")
        end_raw = item["end"].get("dateTime") or item["end"].get("date")

        # All-day events have date strings, not datetimes
        all_day = "dateTime" not in item["start"]
        if all_day:
            start_dt = datetime.fromisoformat(start_raw)
            end_dt = datetime.fromisoformat(end_raw)
        else:
            start_dt = datetime.fromisoformat(start_raw)
            end_dt = datetime.fromisoformat(end_raw)

        events.append({
            "summary": item.get("summary", "(No title)"),
            "start": start_dt,
            "end": end_dt,
            "all_day": all_day,
            "location": item.get("location", ""),
        })

    return events


def split_today_upcoming(events):
    local_now = datetime.now().astimezone()
    today_date = local_now.date()

    today, upcoming = [], []
    for e in events:
        start = e["start"]
        if hasattr(start, "date"):
            event_date = start.date() if not e["all_day"] else start.date()
        else:
            event_date = start

        if event_date == today_date:
            today.append(e)
        else:
            upcoming.append(e)

    return today, upcoming
