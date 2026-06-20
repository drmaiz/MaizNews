from datetime import datetime, timezone, timedelta


def get_events(client, days=7):
    """Get calendar events using MCP Google Calendar connector"""
    try:
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=days)

        result = client.list_events(
            calendarId="primary",
            startTime=now.isoformat(),
            endTime=end.isoformat(),
            pageSize=50,
            orderBy="startTime",
        )

        events = []
        for item in result.get("events", []):
            start_raw = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date")
            end_raw = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")

            if not start_raw:
                continue

            # All-day events have date strings, not datetimes
            all_day = "dateTime" not in item.get("start", {})
            try:
                start_dt = datetime.fromisoformat(start_raw.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_raw.replace('Z', '+00:00'))
            except:
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
    except Exception as e:
        print(f"Error getting calendar events: {e}")
        return []


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
