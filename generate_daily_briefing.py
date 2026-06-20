#!/usr/bin/env python3
"""Generate daily briefing HTML with real data from APIs and MCP services."""

from datetime import datetime

# Real data from MCP and APIs
calendar_events = []

unread_emails = 10
recent_emails = [
    {
        "subject": "Import to drmaiz/maiz-autoresearch has finished!",
        "from": "GitHub <noreply@github.com>",
        "snippet": "The import to https://github.com/drmaiz/maiz-autoresearch has finished! Happy cloning!"
    },
    {
        "subject": "Low balance alert: Your payment was declined",
        "from": "Venmo <venmo@email.venmo.com>",
        "snippet": "Your Venmo Debit Card payment was declined due to low balance."
    },
    {
        "subject": "👤 Ramon, add Jorge F. Gonzalez Jirau, MD, MBA, CPE",
        "from": "LinkedIn <messages-noreply@linkedin.com>",
        "snippet": "Former Chief Medical Officer HCA Florida St. Lucie Hospital"
    }
]

weather = {
    "city": "Jacksonville, FL",
    "temp": 93,
    "feels_like": 99,
    "humidity": 44,
    "wind": 7,
    "condition": "Clear sky"
}

headlines = [
    {"title": "Live Updates: Iran says it's closing Strait of Hormuz again as Hezbollah and Israel trade attacks", "source": "CBS News"},
    {"title": "Trump acknowledges 'real problems' at reflecting pool after $14m makeover, blaming 'vandalism'", "source": "The Guardian"},
    {"title": "Trump says Iran missiles 'aren't the problem' after White House made them central to war rationale", "source": "Fox News"},
    {"title": "Israel continues strikes in Lebanon despite ceasefire with Hezbollah", "source": "politico.eu"},
    {"title": "3 Hikers Die at Grand Canyon Amid 'Dangerous' High Temperatures", "source": "The New York Times"},
    {"title": "Meloni tells Trump to 'focus on your own popularity' as row escalates", "source": "BBC"},
    {"title": "Tom Cotton, the Senate's foremost Iran hawk, is in a Trump-induced jam", "source": "Politico"}
]

quote = {
    "text": "Let us rather run the risk of wearing out than rusting out.",
    "author": "Theodore Roosevelt"
}

# HTML Template
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

def render_email_section(unread_count, recent_emails):
    """Render email summary"""
    email_list = ""
    if recent_emails:
        for email in recent_emails[:5]:
            subject = email["subject"]
            from_addr = email["from"].split('<')[0].strip() if '<' in email["from"] else email["from"]
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
    """Render weather section"""
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

def _get_category_and_emoji(headline):
    """Determine category and emoji based on headline content"""
    headline_lower = headline.lower()

    if "iran" in headline_lower or "israel" in headline_lower or "hezbollah" in headline_lower:
        return "Global Crisis", "🌍"
    elif "trump" in headline_lower or "political" in headline_lower:
        return "Politics", "🏛️"
    elif "death" in headline_lower or "die" in headline_lower:
        return "Breaking", "🔴"
    elif "tech" in headline_lower or "ai" in headline_lower:
        return "Tech", "🟢"
    else:
        return "News", "📰"

def render_news_section(headlines):
    """Render news items"""
    if not headlines:
        return ''

    news_items = ""
    for article in headlines[:7]:
        headline = article["title"]
        source = article["source"]
        category, emoji = _get_category_and_emoji(headline)

        takeaway = f"Key story from {source} — monitor for developments."

        news_items += f"""
    <article class="item">
        <div class="item-emoji">{emoji}</div>
        <div class="item-body">
            <div class="item-meta">
                <span class="category-tag">{category}</span>
                <span class="source-time"><strong>{source}</strong> · Today</span>
            </div>
            <h2 class="headline">{headline}</h2>
            <div class="takeaway">
                <span class="takeaway-arrow">→</span>
                <span class="takeaway-text">{takeaway}</span>
            </div>
        </div>
    </article>
        """

    return news_items

def render_quote_section(quote):
    """Render quote of the day"""
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

# Generate HTML
now = datetime.now()
formatted_date = now.strftime("%A, %B %d, %Y")
current_time = now.strftime("%I:%M %p")

email_html = render_email_section(unread_emails, recent_emails)
weather_html = render_weather_section(weather)
news_html = render_news_section(headlines)
quote_html = render_quote_section(quote)

sections = email_html + weather_html + news_html + quote_html

html = HTML_TEMPLATE.format(
    date=formatted_date,
    formatted_date=formatted_date,
    current_time=current_time,
    sections=sections,
)

# Save file
filename = f"daily-briefing-{now.strftime('%Y-%m-%d')}.html"
with open(filename, "w") as f:
    f.write(html)

print(f"✅ Daily briefing generated: {filename}")
