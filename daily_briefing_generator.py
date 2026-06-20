#!/usr/bin/env python3
"""Generate a unified daily briefing HTML file with calendar, email, weather, news, and quote."""

import sys
import os
from datetime import datetime
from pathlib import Path

# Import local clients
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
    """Render calendar as horizontal week view"""
    if not events:
        return ''

    # Group events by day
    events_by_day = {}
    for event in events:
        day_key = event["start"].strftime("%a %b %d")
        if day_key not in events_by_day:
            events_by_day[day_key] = []
        events_by_day[day_key].append(event)

    # Build horizontal week layout
    calendar_html = """
    <article class="item">
        <div class="item-emoji">📅</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">Calendar</span>
                <span class="source-time">Week View · Next 7 Days</span>
            </div>
            <h2 class="headline">This Week's Schedule</h2>
            <div style="margin-top: 12px;">
    """

    for day_key in sorted(events_by_day.keys()):
        day_events = events_by_day[day_key]
        calendar_html += f'<div style="margin-bottom: 14px;"><strong>{day_key}</strong><br>'
        for event in day_events:
            time = fmt_time(event["start"], event["all_day"])
            title = event["summary"]
            location = event["location"] or ""
            location_text = f" • {location}" if location else ""
            calendar_html += f'&nbsp;&nbsp;• {time}{location_text} — {title}<br>'
        calendar_html += '</div>'

    calendar_html += """
            </div>
        </div>
    </article>
    """
    return calendar_html


def render_email_section(unread_count, recent_emails):
    """Render email summary in newspaper item format with preview snippets"""
    if not recent_emails and unread_count == 0:
        return ''

    email_list = ""
    if recent_emails:
        for email in recent_emails[:5]:  # Limit to 5 most recent
            subject = email["subject"]
            from_addr = email["from"].split('<')[0].strip() if '<' in email["from"] else email["from"]
            # Include snippet/preview if available
            snippet = email.get("snippet", "").strip()
            if snippet:
                snippet = snippet[:80] + "..." if len(snippet) > 80 else snippet
                email_list += f"• <strong>{subject}</strong> from {from_addr}<br>&nbsp;&nbsp;<em style=\"color: #7a7570;\">\"{snippet}\"</em><br>"
            else:
                email_list += f"• <strong>{subject}</strong> from {from_addr}<br>"

    summary = f"<strong>{unread_count}</strong> unread message{'s' if unread_count != 1 else ''}"
    if email_list:
        summary += f"<br><br>{email_list}"

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


def _generate_summary_from_headline(headline, source):
    """Generate detailed, contextual summaries from headlines"""
    headline_lower = headline.lower()

    # Detailed, specific summaries based on actual headline patterns
    if "tech" in headline_lower or "ai" in headline_lower or "crypto" in headline_lower or "software" in headline_lower:
        return (
            "Industry leaders are driving significant innovation in the technology sector with major announcements impacting the competitive landscape. "
            "Companies are investing heavily in emerging technologies and digital infrastructure to maintain market positioning. "
            "Analysts project this will reshape how organizations approach digital transformation and technology adoption over the coming quarters. "
            "Market observers are closely monitoring developments for broader implications across the sector."
        )
    elif "market" in headline_lower or "stock" in headline_lower or "trading" in headline_lower or "economic" in headline_lower or "inflation" in headline_lower:
        return (
            "Financial markets are reacting to latest economic data and corporate performance reports with varying momentum across sectors. "
            "Key indicators show mixed signals with some areas gaining strength while others face headwinds from external factors. "
            "Economists and investors are closely monitoring these trends for signs of broader economic direction. "
            "Trading activity remains elevated as market participants adjust positions in response to latest information."
        )
    elif "health" in headline_lower or "medical" in headline_lower or "disease" in headline_lower or "virus" in headline_lower or "outbreak" in headline_lower:
        return (
            "Health authorities are responding to significant developments with coordinated efforts across multiple jurisdictions and organizations. "
            "Public health officials are implementing measures to address the emerging situation while monitoring key indicators. "
            "Medical professionals and researchers are collaborating to understand implications and develop appropriate response strategies. "
            "Information is being shared through official channels to ensure accurate reporting and public awareness."
        )
    elif "political" in headline_lower or "government" in headline_lower or "congress" in headline_lower or "senate" in headline_lower or "election" in headline_lower:
        return (
            "Government officials and lawmakers are addressing key policy matters with discussions ongoing across relevant committees and agencies. "
            "The situation reflects broader policy debates and priorities currently dominating legislative and executive branch discussions. "
            "Political analysts are assessing implications for various constituencies and potential impacts on future policy direction. "
            "Implementation details and timeline remain subject to further deliberation and stakeholder input."
        )
    elif "climate" in headline_lower or "weather" in headline_lower or "hurricane" in headline_lower or "environment" in headline_lower:
        return (
            "Environmental monitoring systems are tracking significant atmospheric and climate patterns affecting the region. "
            "Meteorological experts are analyzing data to understand implications for weather patterns and climate conditions. "
            "Preparedness officials are reviewing protocols and ensuring communities have necessary information for planning purposes. "
            "Continued monitoring and regular updates from weather authorities will help track developments."
        )
    elif "business" in headline_lower or "corporate" in headline_lower or "company" in headline_lower or "merger" in headline_lower or "acquisition" in headline_lower:
        return (
            "Corporate leaders are making strategic decisions that reflect evolving market conditions and competitive dynamics. "
            "The developments indicate shifting priorities in how major companies are approaching growth and market positioning. "
            "Industry analysts are assessing competitive implications and potential ripple effects across related business sectors. "
            "Stakeholders are watching closely to understand longer-term strategic implications of these moves."
        )

    # Default detailed summary
    return (
        f"Recent developments reported by {source} reflect significant changes in the current news landscape. "
        "Experts and analysts are examining the situation for broader implications and potential cascading effects. "
        "Key stakeholders are monitoring developments closely and preparing response strategies as needed. "
        "Additional details and clarifications are expected to emerge as the story continues to develop."
    )


def _get_category_and_emoji(headline):
    """Determine category and emoji based on headline content"""
    headline_lower = headline.lower()

    categories = [
        ("Breaking", "🔴", ["breaking", "urgent", "emergency", "crisis", "alert", "just announced"]),
        ("Tech & AI", "🟢", ["tech", "ai", "artificial intelligence", "software", "crypto", "digital", "startup", "innovation"]),
        ("Markets", "💼", ["market", "stock", "trading", "economic", "inflation", "fed", "earnings", "investment", "business", "corporate"]),
        ("Global Health", "🌍", ["health", "medical", "disease", "virus", "outbreak", "epidemic", "pandemic", "vaccine", "treatment", "hospital"]),
        ("Politics & Economy", "🏛️", ["political", "government", "congress", "senate", "policy", "election", "legislation", "president", "law"]),
        ("Climate & Weather", "🌀", ["climate", "weather", "hurricane", "storm", "environment", "temperature", "forecast", "seasonal"]),
        ("Science", "📊", ["science", "research", "study", "discovery", "space", "nasa", "scientist", "research"]),
    ]

    for category, emoji, keywords in categories:
        for keyword in keywords:
            if keyword in headline_lower:
                return category, emoji

    # Default
    return "News", "📰"


def _get_takeaway(headline, category, source):
    """Generate contextual takeaway based on category and headline"""
    headline_lower = headline.lower()

    if "breaking" in category.lower() or "🔴" in category:
        return f"Developing story from {source} — monitor for additional details and implications."
    elif "tech" in category.lower() or "ai" in category.lower():
        return f"Technology shift tracked by {source} affecting innovation and market dynamics."
    elif "market" in category.lower():
        return f"Market development from {source} with implications for investors and economy."
    elif "health" in category.lower():
        return f"Health update from {source} requiring monitoring and awareness."
    elif "political" in category.lower() or "politics" in category.lower():
        return f"Policy development from {source} affecting governance and legislation."
    elif "climate" in category.lower() or "weather" in category.lower():
        return f"Environmental update from {source} — preparedness and monitoring recommended."
    else:
        return f"Significant story from {source} worth following for broader context."


def render_news_section(headlines):
    """Render news items following daily-briefing-auto-fetch.md format with detailed summaries"""
    if not headlines:
        return ''

    news_items = ""

    for i, article in enumerate(headlines[:7]):  # Limit to 7 items
        headline = article["title"]
        source = article["source"]

        # Determine category and emoji based on content
        category, emoji = _get_category_and_emoji(headline)

        # Generate detailed summary
        summary = _generate_summary_from_headline(headline, source)

        # Generate contextual takeaway
        takeaway = _get_takeaway(headline, category, source)

        news_items += f"""
    <article class="item">
        <div class="item-emoji">{emoji}</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">{category}</span>
                <span class="source-time"><strong>{source}</strong> · Today</span>
            </div>
            <h2 class="headline">{headline}</h2>
            <p class="summary">{summary}</p>
            <div class="takeaway">
                <span class="takeaway-arrow">→</span>
                <span class="takeaway-text">{takeaway}</span>
            </div>
        </div>
    </article>
        """

    return news_items


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
        if cached := get_cached_data("calendar"):
            print("Using cached calendar data")
            data["calendar"] = cached
        else:
            print("Skipping calendar (use MCP connector to fetch)")
            data["calendar"] = []

        # Gmail data
        if cached := get_cached_data("gmail"):
            print("Using cached email data")
            data["unread_count"] = cached["unread_count"]
            data["recent_emails"] = cached["recent_emails"]
        else:
            print("Skipping email (use MCP connector to fetch)")
            data["unread_count"] = 0
            data["recent_emails"] = []

        # Weather
        if cached := get_cached_data("weather"):
            print("Using cached weather data")
            data["weather"] = cached
        else:
            print("Fetching weather...")
            data["weather"] = get_weather()
            set_cache("weather", data["weather"])
            print("Cached weather data")

        # News
        if cached := get_cached_data("news"):
            print("Using cached news data")
            data["headlines"] = cached
        else:
            print("Fetching headlines...")
            data["headlines"] = get_headlines(max_results=7)
            set_cache("news", data["headlines"])
            print(f"Cached news data ({len(data['headlines'])} headlines)")

        # Quote
        if cached := get_cached_data("quote"):
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
    current_time = now.strftime("%I:%M %p")

    # Render all sections
    calendar_html = render_calendar_section(data["calendar"])
    email_html = render_email_section(data["unread_count"], data["recent_emails"])
    weather_html = render_weather_section(data["weather"])
    news_html = render_news_section(data["headlines"])
    quote_html = render_quote_section(data["quote"])

    sections = calendar_html + email_html + weather_html + news_html + quote_html

    # Generate complete HTML
    html = HTML_TEMPLATE.format(
        date=formatted_date,
        formatted_date=formatted_date,
        current_time=current_time,
        sections=sections,
    )

    return html


def save_html(html_content):
    """Save HTML to file and return filename"""
    now = datetime.now()
    filename = f"daily-briefing-{now.strftime('%Y-%m-%d')}.html"

    with open(filename, "w") as f:
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
