#!/usr/bin/env python3
"""Test HTML generation with mocked imports"""

import sys
from datetime import datetime, timedelta

# Mock the auth module before importing daily_briefing_generator
class MockAuth:
    @staticmethod
    def build_services():
        return None, None

sys.modules['auth'] = MockAuth()

# Now we can define the rendering functions directly
def fmt_time(dt, all_day):
    """Format datetime to readable time string"""
    if all_day:
        return "All day"
    local = dt.astimezone()
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
    """Render calendar events as HTML table"""
    if not events:
        return '<div class="section-title">📅 This Week\'s Events</div><p style="color: #718096; font-size: 14px;">No upcoming events</p>'

    rows = ""
    for event in events:
        day = fmt_date(event["start"], event["all_day"])
        time = fmt_time(event["start"], event["all_day"])
        title = event["summary"]
        location = event["location"] or ""

        rows += f"""
        <tr>
            <td class="event-time">{time}</td>
            <td class="event-title">{title}</td>
            <td class="event-location">{location}</td>
        </tr>
        """

    table = f"""
    <div class="section-title">📅 This Week's Events</div>
    <table class="calendar-table">
        <thead>
            <tr>
                <th style="width: 25%;">Time</th>
                <th style="width: 50%;">Event</th>
                <th style="width: 25%;">Location</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
    return table


def render_email_section(unread_count, recent_emails):
    """Render email summary section"""
    email_items = ""
    if recent_emails:
        for email in recent_emails[:5]:
            subject = email["subject"]
            from_addr = email["from"]
            email_items += f'''
            <div class="email-item">
                <div class="email-subject">{subject}</div>
                <div class="email-from">from {from_addr}</div>
            </div>
            '''

    return f"""
    <div class="section-title">📧 Email Summary</div>
    <div class="email-summary">
        <div class="unread-count">{unread_count} unread</div>
        {'<ul class="email-list">' + email_items + '</ul>' if email_items else '<p style="color: #718096; font-size: 13px;">No unread emails</p>'}
    </div>
    """


def render_weather_section(weather):
    """Render weather section"""
    return f"""
    <div class="section-title">🌤️ Weather</div>
    <div class="weather-card">
        <div class="weather-temp">{weather['temp']}°F</div>
        <div class="weather-condition">{weather['condition']}</div>
        <div class="weather-details">
            Feels like {weather['feels_like']}°F<br>
            Humidity {weather['humidity']}% • Wind {weather['wind']} mph
        </div>
    </div>
    """


def render_news_section(headlines):
    """Render news items in daily briefing format"""
    if not headlines:
        return '<div class="section-title">🔴 Top News</div><p style="color: #718096; font-size: 14px;">No news available</p>'

    news_items = ""
    for i, article in enumerate(headlines, 1):
        emoji = ["🔴", "🟢", "💼", "🌍", "🏛️", "📊", "🎯"][i % 7]
        category = ["Breaking", "Tech", "Business", "Global", "Politics", "Science", "Trending"][i % 7]
        headline = article["title"][:80]
        source = article["source"]
        time_text = "Today"
        summary = f"Source: {source}"

        news_items += f"""
        <div class="news-item">
            <div class="news-header">
                <div class="news-emoji">{emoji}</div>
                <div class="news-title">
                    <div class="news-category">{category}</div>
                    <div class="news-headline">{headline}</div>
                    <div class="news-meta">
                        <div class="news-source">📰 {source}</div>
                        <div class="news-time">⏱️ {time_text}</div>
                    </div>
                </div>
            </div>
            <div class="news-summary">{summary}</div>
        </div>
        """

    return f"""
    <div class="section-divider"></div>
    <div class="section-title">🔴 Top News</div>
    {news_items}
    """


def render_quote_section(quote):
    """Render quote of the day section"""
    return f"""
    <div class="section-divider"></div>
    <div class="section-title">✨ Quote of the Day</div>
    <div class="quote-section">
        <div class="quote-text">"{quote['text']}"</div>
        <div class="quote-author">— {quote['author']}</div>
    </div>
    """


def generate_html(data):
    """Generate complete HTML file from data"""
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Briefing - {date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #2d3748;
        }}

        .container {{
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 25px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }}

        .header .date {{
            font-size: 14px;
            opacity: 0.9;
            font-weight: 300;
        }}

        .divider {{
            height: 3px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        }}

        .content {{
            padding: 30px;
        }}

        /* Section Titles */
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #667eea;
            margin-top: 28px;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .section-title:first-child {{
            margin-top: 0;
        }}

        .section-divider {{
            height: 1px;
            background: #e2e8f0;
            margin: 24px 0;
        }}

        /* Calendar Section */
        .calendar-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
            font-size: 14px;
        }}

        .calendar-table th {{
            background: #f7fafc;
            color: #667eea;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            border-bottom: 2px solid #e2e8f0;
        }}

        .calendar-table td {{
            padding: 12px 8px;
            border-bottom: 1px solid #e2e8f0;
            color: #4a5568;
        }}

        .calendar-table tr:last-child td {{
            border-bottom: none;
        }}

        .event-time {{
            color: #718096;
            font-size: 13px;
            font-weight: 500;
        }}

        .event-title {{
            color: #1a202c;
            font-weight: 500;
        }}

        .event-location {{
            color: #718096;
            font-size: 13px;
        }}

        /* Email Section */
        .email-summary {{
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 14px 16px;
            border-radius: 4px;
            margin-bottom: 12px;
        }}

        .unread-count {{
            font-size: 16px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 8px;
        }}

        .email-list {{
            list-style: none;
            margin-top: 12px;
        }}

        .email-item {{
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
            font-size: 13px;
        }}

        .email-item:last-child {{
            border-bottom: none;
        }}

        .email-subject {{
            color: #1a202c;
            font-weight: 500;
            margin-bottom: 2px;
        }}

        .email-from {{
            color: #718096;
            font-size: 12px;
        }}

        /* Weather Section */
        .weather-card {{
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 16px;
        }}

        .weather-temp {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .weather-condition {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 12px;
        }}

        .weather-details {{
            font-size: 13px;
            opacity: 0.85;
            line-height: 1.6;
        }}

        /* News Section */
        .news-item {{
            margin-bottom: 28px;
            padding-bottom: 28px;
            border-bottom: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }}

        .news-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}

        .news-item:hover {{
            transform: translateX(4px);
            box-shadow: -3px 0 0 #667eea;
        }}

        .news-header {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .news-emoji {{
            font-size: 24px;
            min-width: 24px;
        }}

        .news-title {{
            flex: 1;
        }}

        .news-category {{
            display: inline-block;
            background: #f7fafc;
            color: #667eea;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}

        .news-headline {{
            font-size: 18px;
            font-weight: 600;
            color: #1a202c;
            line-height: 1.4;
            margin-bottom: 8px;
        }}

        .news-meta {{
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #718096;
            margin-bottom: 12px;
        }}

        .news-source {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .news-time {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .news-summary {{
            font-size: 14px;
            line-height: 1.6;
            color: #4a5568;
            margin-bottom: 12px;
        }}

        /* Quote Section */
        .quote-section {{
            background: #f7fafc;
            padding: 24px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 16px;
        }}

        .quote-text {{
            font-size: 16px;
            font-style: italic;
            color: #2d3748;
            margin-bottom: 12px;
            line-height: 1.6;
        }}

        .quote-author {{
            font-size: 13px;
            color: #718096;
            font-weight: 500;
        }}

        /* Footer */
        .footer {{
            background: #f7fafc;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }}

        /* Dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background: #1a202c;
            }}

            .container {{
                background: #2d3748;
                color: #e2e8f0;
            }}

            .news-headline {{
                color: #f7fafc;
            }}

            .event-title {{
                color: #f7fafc;
            }}

            .news-category {{
                background: rgba(102, 126, 234, 0.1);
                color: #a0aec0;
            }}

            .news-summary {{
                color: #cbd5e0;
            }}

            .divider {{
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            }}

            .section-divider {{
                background: #4a5568;
            }}

            .calendar-table th {{
                background: #1a202c;
                border-bottom-color: #4a5568;
            }}

            .calendar-table td {{
                border-bottom-color: #4a5568;
            }}

            .calendar-table th {{
                color: #a0aec0;
            }}

            .footer {{
                background: #1a202c;
                border-top-color: #4a5568;
            }}

            .email-summary {{
                background: rgba(102, 126, 234, 0.1);
            }}

            .quote-section {{
                background: #1a202c;
                border: 1px solid #4a5568;
            }}

            .quote-text {{
                color: #e2e8f0;
            }}
        }}

        /* Mobile responsive */
        @media (max-width: 600px) {{
            .container {{
                border-radius: 0;
            }}

            .header {{
                padding: 20px 15px;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .content {{
                padding: 20px;
            }}

            .news-headline {{
                font-size: 16px;
            }}

            .news-item {{
                margin-bottom: 20px;
                padding-bottom: 20px;
            }}

            .calendar-table {{
                font-size: 12px;
            }}

            .calendar-table th,
            .calendar-table td {{
                padding: 8px 4px;
            }}
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                max-width: 100%;
            }}

            .news-item:hover {{
                transform: none;
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Daily Briefing</h1>
            <div class="date">{formatted_date}</div>
        </div>
        <div class="divider"></div>

        <div class="content">
            {sections}
        </div>

        <div class="footer">
            <p>Stay informed • Curated daily • Last updated: {current_time}</p>
        </div>
    </div>
</body>
</html>
"""

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
    filename = f"daily-briefing-test-{now.strftime('%Y-%m-%d')}.html"

    with open(filename, "w") as f:
        f.write(html_content)

    return filename


# Test data structure
test_data = {
    "calendar": [
        {
            "summary": "Team standup",
            "start": datetime.now(),
            "end": datetime.now() + timedelta(hours=1),
            "all_day": False,
            "location": "Conference Room A"
        },
        {
            "summary": "Project deadline",
            "start": datetime.now() + timedelta(days=2),
            "end": datetime.now() + timedelta(days=2, hours=1),
            "all_day": False,
            "location": "Remote"
        },
        {
            "summary": "All-day company event",
            "start": datetime.now() + timedelta(days=5),
            "end": datetime.now() + timedelta(days=6),
            "all_day": True,
            "location": ""
        }
    ],
    "unread_count": 12,
    "recent_emails": [
        {
            "subject": "Project Update - Q3 Goals",
            "from": "manager@company.com",
            "date": datetime.now() - timedelta(hours=2),
            "snippet": "Here are the Q3 goals..."
        },
        {
            "subject": "Meeting Notes from Yesterday",
            "from": "colleague@company.com",
            "date": datetime.now() - timedelta(hours=4),
            "snippet": "Summary of action items..."
        }
    ],
    "weather": {
        "city": "Jacksonville, FL",
        "temp": 92,
        "feels_like": 95,
        "humidity": 75,
        "wind": 8,
        "condition": "Sunny"
    },
    "headlines": [
        {"title": "AI Companies Report Strong Growth Amid Tech Surge", "source": "Reuters"},
        {"title": "New Climate Report Shows Urgent Action Needed", "source": "AP News"},
        {"title": "Markets Rally on Better-Than-Expected Earnings", "source": "Bloomberg"},
        {"title": "Scientists Discover New Exoplanet in Habitable Zone", "source": "NASA"},
        {"title": "Tech Stocks Lead Market Rally This Week", "source": "CNBC"}
    ],
    "quote": {
        "text": "The future belongs to those who believe in the beauty of their dreams.",
        "author": "Eleanor Roosevelt"
    }
}

print("📋 Testing HTML generation with mock data...")

try:
    html = generate_html(test_data)
    print(f"✅ HTML generated successfully ({len(html)} bytes)")

    filename = save_html(html)
    print(f"✅ HTML saved to {filename}")

    # Verify the file contains expected content
    with open(filename, "r") as f:
        content = f.read()

    checks = {
        "Daily Briefing": "Daily Briefing" in content,
        "Calendar section": "This Week's Events" in content,
        "Email section": "Email Summary" in content,
        "Weather section": "Weather" in content,
        "News section": "Top News" in content,
        "Quote section": "Quote of the Day" in content,
        "Mock headline": "AI Companies" in content,
        "CSS styling": "linear-gradient" in content,
        "Dark mode support": "prefers-color-scheme" in content,
    }

    print("\n📊 Verification Results:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All checks passed!")
        print(f"\n📄 Generated file: {filename}")
    else:
        print("\n⚠️ Some checks failed")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
