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

        /* MEDICAL CALLOUT */
        .medical-callout {{
            background: #eaf2fb;
            border-left: 3px solid var(--medical);
            padding: 9px 12px;
            border-radius: 0 3px 3px 0;
            margin-bottom: 12px;
        }}

        .medical-callout-label {{
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--medical);
            margin-bottom: 3px;
        }}

        .medical-callout-text {{
            font-size: 12px;
            color: #1a3a5a;
            line-height: 1.5;
        }}

        /* FOOTER */
        footer {{
            border-top: 3px double var(--ink);
            margin: 0 48px;
            padding: 16px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--muted);
        }}

        footer strong {{ color: var(--ink); }}

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
            .medical-callout {{ background: #0d1f2e; }}
            .medical-callout-text {{ color: #9dc3e6; }}
            .masthead {{ border-color: var(--rule); }}
            .section-ribbon {{ border-color: var(--rule); }}
            footer {{ border-color: var(--rule); }}
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
            footer {{ margin: 0 20px; flex-direction: column; gap: 6px; text-align: center; }}
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
        <div>{story_summary}</div>
        <div style="font-size: 10px; margin-top: 4px;">Sources: {sources}</div>
    </div>
</header>

<nav class="section-ribbon">
    {nav_sections}
</nav>

<main class="container">
    {sections}
</main>

<footer>
    <span>📰 <strong>The Morning Read</strong> — Daily Briefing</span>
    <span>{formatted_date} · {location} Edition</span>
    <span>Sources: {sources}</span>
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


def _detect_health_alert(headline, summary):
    """Detect if article contains health/medical emergency content"""
    health_keywords = ['ebola', 'virus', 'outbreak', 'pandemic', 'disease', 'epidemic', 
                       'health', 'clinical', 'medical', 'pathogen', 'cdc', 'who']
    text = (headline + " " + summary).lower()
    return any(keyword in text for keyword in health_keywords)


def _get_article_category(headline, summary):
    """Intelligently categorize article"""
    text = (headline + " " + summary).lower()
    
    categories = {
        "Global Health": ["ebola", "virus", "outbreak", "disease", "epidemic", "pandemic", "health", "who", "cdc"],
        "Breaking": ["breaking", "alert", "just in", "urgent", "immediate", "developing"],
        "Markets": ["market", "stock", "trade", "economic", "inflation", "oil", "price"],
        "Tech & AI": ["ai", "tech", "artificial intelligence", "claude", "model", "technology"],
        "Politics": ["political", "congress", "senate", "trump", "biden", "government"],
        "Global": ["international", "global", "country", "nation", "foreign"],
    }
    
    for category, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return category
    return "News"


def _get_article_emoji(category):
    """Get emoji for article category"""
    emoji_map = {
        "Breaking": "🔴",
        "Markets": "💼",
        "Global Health": "🌍",
        "Tech & AI": "🟢",
        "Politics": "🏛️",
        "Global": "🌍",
        "Science": "🔬",
    }
    return emoji_map.get(category, "📰")


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
    """Render news items in newspaper format with contextual summaries and health alerts"""
    if not headlines:
        return ''

    parts = []
    for article in headlines:
        category = _get_article_category(article.get("title", ""), 
                                         article.get("description", ""))
        is_health_alert = _detect_health_alert(article.get("title", ""), 
                                               article.get("description", ""))
        
        emoji = _get_article_emoji(category)
        headline = article.get("title", "(No title)")
        source = article.get("source", "Unknown")
        summary_text = article.get("description") or article.get("summary") or article.get("snippet") or ''
        
        # Truncate summary to reasonable length
        if len(summary_text) > 450:
            summary_text = summary_text[:447] + '...'

        summary_html = f"<p class=\"summary\">{summary_text}</p>" if summary_text else ""
        
        # Add medical callout for health alerts
        medical_callout = ""
        if is_health_alert and category == "Global Health":
            medical_callout = """
            <div class="medical-callout">
                <div class="medical-callout-label">⚕️ Health Alert</div>
                <div class="medical-callout-text">Monitor this story for public health implications. Follow updates from <strong>WHO</strong> and <strong>CDC</strong>.</div>
            </div>
            """

        takeaway = f"Source: <strong>{source}</strong>"

        tag_class = "breaking" if category == "Breaking" else ("medical" if category == "Global Health" else "")
        
        parts.append(f"""
    <article class="item">
        <div class="item-emoji">{emoji}</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag {tag_class}">{category}</span>
                <span class="source-time"><strong>{source}</strong> · Today</span>
            </div>
            <h2 class="headline">{headline}</h2>
            {summary_html}
            {medical_callout}
            <div class="takeaway">
                <span class="takeaway-arrow">→</span>
                <span class="takeaway-text">{takeaway}</span>
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
            data["headlines"] = get_headlines(max_results=6)
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
    
    location = "South Florida"  # Make configurable as needed
    
    # Count news items (calendar, email, weather, news)
    num_news = len(data.get("headlines", []))
    num_calendar = len(data.get("calendar", []))
    story_count = num_news + (3 if num_calendar > 0 else 0)  # 3 for calendar, email, weather
    story_summary = f"{story_count} stories · Curated for {location}"
    
    # Extract unique sources from headlines
    sources_set = set()
    for article in data.get("headlines", []):
        source = article.get("source", "")
        if source:
            sources_set.add(source)
    sources = " · ".join(sorted(sources_set)[:5]) or "AP · NBC · CNN"
    
    # Build nav sections dynamically
    nav_items = []
    if data.get("calendar"):
        nav_items.append("<span>📅 Calendar</span>")
    if data.get("unread_count", 0) > 0:
        nav_items.append("<span>📧 Email</span>")
    if data.get("weather"):
        nav_items.append("<span>🌤️ Weather</span>")
    
    # Add category-based nav from news
    news_categories = set()
    for article in data.get("headlines", []):
        category = _get_article_category(article.get("title", ""), article.get("description", ""))
        emoji = _get_article_emoji(category)
        news_categories.add(f"<span>{emoji} {category}</span>")
    
    nav_sections = "".join(nav_items) + "".join(sorted(news_categories)[:3])

    # Render all sections
    calendar_html = render_calendar_section(data["calendar"]) if data.get("calendar") is not None else ''
    email_html = render_email_section(data.get("unread_count", 0), data.get("recent_emails", []))
    weather_html = render_weather_section(data["weather"]) if data.get("weather") is not None else ''
    news_html = render_news_section(data.get("headlines", []))
    quote_html = render_quote_section(data.get("quote", {"text":"","author":""}))

    sections = calendar_html + email_html + weather_html + news_html + quote_html

    # Generate complete HTML
    html = HTML_TEMPLATE.format(
        date=formatted_date,
        formatted_date=formatted_date,
        current_time=current_time,
        location=location,
        story_summary=story_summary,
        sources=sources,
        nav_sections=nav_sections,
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
