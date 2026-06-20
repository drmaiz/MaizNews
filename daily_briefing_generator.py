#!/usr/bin/env python3
"""Generate a unified daily briefing HTML file with calendar, email, weather, news, and quote."""

import sys
import os
from datetime import datetime
from pathlib import Path

# Import local clients
from auth import build_services
from calendar_client import get_events, split_today_upcoming
from gmail_client import get_unread_count, get_recent_unread
from weather_client import get_weather
from news_client import get_headlines
from quote_client import get_quote
from cache import get_cached_data, set_cache

# HTML Template and styling
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Briefing — {date}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700;800&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        :root {{
            --ink: #1a1a2e;
            --paper: #f7f6f2;
            --accent: #c8102e;
            --rule: #d4cfc8;
            --muted: #7a7570;
            --highlight-bg: #fff8f0;
            --medical: #1a5276;
        }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--paper);
            color: var(--ink);
            min-height: 100vh;
        }}

        /* MASTHEAD */
        .masthead {{
            border-bottom: 3px double var(--ink);
            padding: 28px 48px 20px;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 16px;
        }}

        .masthead-left {{ flex: 1; }}

        .edition-label {{
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 4px;
        }}

        .masthead-title {{
            font-family: 'Playfair Display', serif;
            font-size: 42px;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.5px;
        }}

        .masthead-right {{
            text-align: right;
            font-size: 11px;
            color: var(--muted);
            line-height: 1.7;
        }}

        .masthead-date {{
            font-weight: 600;
            font-size: 13px;
            color: var(--ink);
        }}

        /* SECTION RIBBON */
        .section-ribbon {{
            border-top: 1px solid var(--ink);
            border-bottom: 1px solid var(--ink);
            padding: 6px 48px;
            display: flex;
            gap: 24px;
            overflow-x: auto;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--muted);
        }}

        .section-ribbon span {{ white-space: nowrap; cursor: pointer; }}
        .section-ribbon span:hover {{ color: var(--accent); }}

        /* MAIN LAYOUT */
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 48px 60px;
        }}

        /* NEWS ITEM */
        .item {{
            padding: 28px 0;
            border-bottom: 1px solid var(--rule);
            display: grid;
            grid-template-columns: 56px 1fr;
            gap: 0 20px;
        }}

        .item:last-child {{ border-bottom: none; }}

        .item-emoji {{
            font-size: 28px;
            line-height: 1;
            padding-top: 4px;
            text-align: center;
        }}

        .item-body {{ }}

        .item-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
            flex-wrap: wrap;
        }}

        .category-tag {{
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            background: var(--ink);
            color: #fff;
            padding: 2px 8px;
            border-radius: 2px;
        }}

        .category-tag.medical {{ background: var(--medical); }}
        .category-tag.breaking {{ background: var(--accent); }}

        .source-time {{
            font-size: 11px;
            color: var(--muted);
        }}

        .source-time strong {{ color: var(--ink); font-weight: 600; }}

        .headline {{
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 10px;
            color: var(--ink);
        }}

        .summary {{
            font-size: 14px;
            line-height: 1.7;
            color: #3a3a4a;
            margin-bottom: 12px;
        }}

        .takeaway {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            background: var(--highlight-bg);
            border-left: 3px solid var(--accent);
            padding: 9px 12px;
            border-radius: 0 3px 3px 0;
        }}

        .takeaway-arrow {{
            font-weight: 700;
            color: var(--accent);
            font-size: 14px;
            flex-shrink: 0;
            margin-top: 1px;
        }}

        .takeaway-text {{
            font-size: 13px;
            font-weight: 500;
            color: #3a2a1a;
            line-height: 1.5;
        }}

        /* DARK MODE */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --ink: #f0ece4;
                --paper: #16161e;
                --rule: #2e2d3a;
                --muted: #7a7888;
                --highlight-bg: #1e1c2a;
            }}

            .category-tag {{ background: #f0ece4; color: #16161e; }}
            .category-tag.medical {{ background: #2e6da4; color: #fff; }}
            .category-tag.breaking {{ background: var(--accent); color: #fff; }}
            .masthead {{ border-color: var(--rule); }}
            .section-ribbon {{ border-color: var(--rule); }}
        }}

        /* MOBILE */
        @media (max-width: 640px) {{
            .masthead {{ padding: 20px 20px 14px; flex-direction: column; align-items: flex-start; }}
            .masthead-right {{ text-align: left; }}
            .masthead-title {{ font-size: 30px; }}
            .section-ribbon {{ padding: 6px 20px; }}
            .container {{ padding: 0 20px 40px; }}
            .item {{ grid-template-columns: 40px 1fr; gap: 0 12px; }}
            .headline {{ font-size: 18px; }}
        }}

        @media print {{
            .takeaway {{ background: #fef5ec; }}
        }}
    </style>
</head>
<body>

<header class="masthead">
    <div class="masthead-left">
        <div class="edition-label">Daily Intelligence Briefing</div>
        <div class="masthead-title">The Morning Read</div>
    </div>
    <div class="masthead-right">
        <div class="masthead-date">{formatted_date}</div>
        <div>Personal Edition · Curated for You</div>
        <div style="font-size: 10px; margin-top: 4px;">Last updated: {current_time}</div>
    </div>
</header>

<nav class="section-ribbon">
    <span>📅 Calendar</span>
    <span>📧 Email</span>
    <span>🌤️ Weather</span>
    <span>🔴 News</span>
    <span>✨ Quote</span>
</nav>

<main class="container">
    {sections}
</main>

<footer style="border-top: 3px double var(--ink); margin: 0 48px; padding: 16px 0; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: var(--muted);">
    <span>📰 <strong style="color: var(--ink);">The Morning Read</strong> — Daily Briefing</span>
    <span>{formatted_date} · Personal Edition</span>
</footer>

</body>
</html>
"""


def fmt_time(dt, all_day):
    """Format datetime to readable time string"""
    if all_day:
        return "All day"
    local = dt.astimezone()
    # Strip leading zero from hour (8:30 AM instead of 08:30 AM)
    time_str = local.strftime("%I:%M %p")
    if time_str[0] == "0":
        time_str = time_str[1:]
    return time_str


def fmt_date(dt, all_day=False):
    """Format datetime to readable date string"""
    if all_day:
        return dt.strftime("%a %b %d").lstrip("0").replace(" 0", " ")
    local = dt.astimezone()
    return local.strftime("%a %b %d").lstrip("0").replace(" 0", " ")


def render_calendar_section(events):
    """Render calendar events in a week-view schedule format (single item)."""
    if not events:
        return ''

    # Build a single article with a weekly schedule listing
    parts = []
    for event in events:
        day = fmt_date(event["start"], event["all_day"])
        time = fmt_time(event["start"], event["all_day"])
        title = event.get("summary", "(No title)")
        location = event.get("location") or "TBD"

        if event.get("all_day"):
            parts.append(f'<div style="margin-bottom: 14px;"><strong>{day}</strong><br>&nbsp;&nbsp;• All day • {title} — {location}<br></div>')
        else:
            parts.append(f'<div style="margin-bottom: 14px;"><strong>{day}</strong><br>&nbsp;&nbsp;• {time} • {location} — {title}<br></div>')

    events_html = "".join(parts)

    return f"""
    <article class="item">
        <div class="item-emoji">📅</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">Calendar</span>
                <span class="source-time">Week View · Next 7 Days</span>
            </div>
            <h2 class="headline">This Week's Schedule</h2>
            <div style="margin-top: 12px;">
{events_html}
            </div>
        </div>
    </article>
        """


def render_email_section(unread_count, recent_emails):
    """Render email summary in newspaper item format"""
    if not recent_emails and unread_count == 0:
        return ''

    items = []
    if recent_emails:
        for email in recent_emails[:5]:  # Show up to 5 recent
            subject = email.get("subject", "(No subject)")
            from_addr = email.get("from", "")
            # extract name if present
            if '<' in from_addr:
                from_display = from_addr.split('<')[0].strip()
            else:
                from_display = from_addr
            snippet = email.get("snippet") or ''
            # truncate snippet to ~140 chars
            if len(snippet) > 140:
                snippet = snippet[:137] + '...'
            if snippet:
                items.append(f'• <strong>{subject}</strong> from {from_display}<br>&nbsp;&nbsp;<em style="color: #7a7570;">"{snippet}"</em><br>')
            else:
                items.append(f'• <strong>{subject}</strong> from {from_display}<br>')

    summary = f"<strong>{unread_count}</strong> unread message{'s' if unread_count != 1 else ''}"
    if items:
        summary += "<br><br>" + "".join(items)

    return f"""
    <article class="item">
        <div class="item-emoji">📧</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">Email</span>
                <span class="source-time">Gmail · Recent</span>
            </div>
            <h2 class="headline">{unread_count} Unread Messages</h2>
            <p class="summary">{summary}</p>
        </div>
    </article>
    """


def render_weather_section(weather):
    """Render weather section in newspaper item format"""
    summary = f"""<strong>{weather['temp']}°F</strong> — {weather['condition']}<br>
Feels like {weather['feels_like']}°F • Humidity {weather['humidity']}% • Wind {weather['wind']} mph"""

    return f"""
    <article class="item">
        <div class="item-emoji">🌤️</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">Weather</span>
                <span class="source-time">{weather['city']} · Live</span>
            </div>
            <h2 class="headline">Current Conditions</h2>
            <p class="summary">{summary}</p>
        </div>
    </article>
    """


def render_news_section(headlines):
    """Render news items in newspaper format with a short summary when available"""
    if not headlines:
        return ''

    parts = []
    for i, article in enumerate(headlines, 1):
        emoji = ["🔴", "🟢", "💼", "🌍", "🏛️", "📊", "🎯"][i % 7]
        # prefer category from article if provided
        category = article.get("category") or ["Breaking", "Tech & AI", "Markets", "Global", "Politics", "Science", "Trending"][i % 7]
        headline = article.get("title", "(No title)")
        source = article.get("source", "")
        # try multiple keys for a summary/description
        summary_text = article.get("description") or article.get("summary") or article.get("snippet") or article.get("content") or ''
        if len(summary_text) > 400:
            summary_text = summary_text[:397] + '...'

        takeaway = f"Source: <strong>{source}</strong>"

        summary_html = f"<p class=\"summary\">{summary_text}</p>" if summary_text else ""

        parts.append(f"""
    <article class=\"item\">
        <div class=\"item-emoji\">{emoji}</div>
        <div class=\"item-body\">
            <div class=\"item-meta\">
                <span class=\"category-tag\">{category}</span>
                <span class=\"source-time\"><strong>{source}</strong> · Today</span>
            </div>
            <h2 class=\"headline\">{headline}</h2>
            {summary_html}
            <div class=\"takeaway\">
                <span class=\"takeaway-arrow\">→</span>
                <span class=\"takeaway-text\">{takeaway}</span>
            </div>
        </div>
    </article>
        """)

    return "".join(parts)


def render_quote_section(quote):
    """Render quote of the day in newspaper format"""
    return f"""
    <article class="item">
        <div class="item-emoji">✨</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">Inspiration</span>
                <span class="source-time">Daily Quote · Zenquotes</span>
            </div>
            <h2 class="headline" style="font-style: italic;">"{quote['text']}"</h2>
            <p class="summary">— {quote['author']}</p>
        </div>
    </article>
    """


def fetch_all_data():
    """Fetch all required data with caching"""
    data = {}

    try:
        # Try calendar from cache first
        if (cached := get_cached_data("calendar")) is not None:
            print("Using cached calendar data")
            data["calendar"] = cached
        else:
            print("Fetching calendar events...")
            calendar_service, gmail_service = build_services()
            events = get_events(calendar_service, days=7)
            data["calendar"] = events
            set_cache("calendar", events)
            print(f"Cached calendar data ({len(events)} events)")

        # Gmail data
        if (cached := get_cached_data("gmail")) is not None:
            print("Using cached email data")
            data["unread_count"] = cached["unread_count"]
            data["recent_emails"] = cached["recent_emails"]
        else:
            print("Fetching email data...")
            if "gmail_service" not in locals():
                calendar_service, gmail_service = build_services()
            unread_count = get_unread_count(gmail_service)
            recent_emails = get_recent_unread(gmail_service, max_results=5)
            data["unread_count"] = unread_count
            data["recent_emails"] = recent_emails
            set_cache("gmail", {"unread_count": unread_count, "recent_emails": recent_emails})
            print(f"Cached email data ({unread_count} unread)")

        # Weather
        if (cached := get_cached_data("weather")) is not None:
            print("Using cached weather data")
            data["weather"] = cached
        else:
            print("Fetching weather...")
            data["weather"] = get_weather()
            set_cache("weather", data["weather"])
            print("Cached weather data")

        # News
        if (cached := get_cached_data("news")) is not None:
            print("Using cached news data")
            data["headlines"] = cached
        else:
            print("Fetching headlines...")
            data["headlines"] = get_headlines(max_results=7)
            set_cache("news", data["headlines"])
            print(f"Cached news data ({len(data['headlines'])} headlines)")

        # Quote
        if (cached := get_cached_data("quote")) is not None:
            print("Using cached quote data")
            data["quote"] = cached
        else:
            print("Fetching quote...")
            data["quote"] = get_quote()
            set_cache("quote", data["quote"])
            print("Cached quote data")

    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return None

    return data


def generate_html(data):
    """Generate complete HTML file from data"""
    now = datetime.now()
    formatted_date = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p").lstrip("0")

    # Render all sections
    calendar_html = render_calendar_section(data["calendar"]) if data.get("calendar") is not None else ''
    email_html = render_email_section(data.get("unread_count", 0), data.get("recent_emails", []))
    weather_html = render_weather_section(data["weather"]) if data.get("weather") is not None else ''
    news_html = render_news_section(data.get("headlines", []))
    quote_html = render_quote_section(data.get("quote", {"text":"","author":""}))

    sections = calendar_html + email_html + weather_html + news_html + quote_html

    # Count items for masthead (kept for compatibility but not displayed in template)
    item_count = len([x for x in [calendar_html, email_html, weather_html, news_html, quote_html] if x])

    # Generate complete HTML
    html = HTML_TEMPLATE.format(
        date=formatted_date,
        formatted_date=formatted_date,
        current_time=current_time,
        item_count=item_count,
        sections=sections,
    )

    return html


def save_html(html_content):
    """Save HTML to file and return filename"""
    now = datetime.now()
    filename = f"daily-briefing-{now.strftime('%Y-%m-%d')}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filename


def main():
    """Main entry point"""
    print("🔄 Generating daily briefing...")

    # Fetch data
    data = fetch_all_data()
    if not data:
        print("❌ Failed to fetch data", file=sys.stderr)
        sys.exit(1)

    # Generate HTML
    html = generate_html(data)

    # Save to file
    filename = save_html(html)
    print(f"✅ Daily briefing saved to {filename}")

    return filename


if __name__ == "__main__":
    main()
