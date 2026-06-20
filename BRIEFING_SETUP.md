# Daily Unified Briefing System - Setup Guide

This system merges personal data (calendar, email, weather) with news into a single, beautiful HTML daily briefing.

## What It Generates

A complete, self-contained HTML file (no external dependencies) that includes:

- **This Week's Calendar Events** – All upcoming events in a clean table format
- **Email Summary** – Unread count and recent unread email subjects
- **Current Weather** – Temperature, condition, humidity, wind speed
- **Top News** – 5-7 news headlines in an engaging format
- **Quote of the Day** – Inspirational daily quote

All sections are styled with:
- Responsive design (mobile & desktop)
- Dark mode support
- Print-friendly styling
- Smooth hover effects

## Quick Start

### 1. Prerequisites

You need:
- Python 3.8+
- A Google Cloud project with Calendar & Gmail APIs enabled
- OAuth 2.0 credentials as `credentials.json`

### 2. Install Dependencies

```bash
cd MaizNews/
pip install -r requirements.txt
```

### 3. Setup Google Credentials

If you don't have `credentials.json` yet:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable these APIs:
   - Google Calendar API
   - Gmail API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download JSON and save as `credentials.json` in this directory

### 4. Generate Your First Briefing

```bash
python daily_briefing_generator.py
```

This will:
- Open a browser for Google authentication (first run only)
- Fetch your calendar, email, weather, and news
- Generate `daily-briefing-2026-06-20.html`
- Open in your default browser

### 5. View the Result

Open the generated HTML file in your browser. Try:
- **Light mode** – Default view
- **Dark mode** – Check system preference or DevTools
- **Mobile view** – Resize browser to test responsiveness
- **Print** – Cmd/Ctrl+P to test print styling

## Configuration

### Customize Weather Location

Edit `weather_client.py`:

```python
LATITUDE = 30.3322    # Your latitude
LONGITUDE = -81.6557  # Your longitude
CITY = "Jacksonville, FL"  # Your city name
```

### Customize News Sources

By default, uses Google News RSS. To customize, edit `news_client.py`:

```python
RSS_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
```

### Cache Settings

Data is cached to avoid repeated API calls within the same day:

```python
# Cache expiry times (seconds):
"calendar": 86400,  # 24 hours
"gmail": 3600,      # 1 hour
"weather": 3600,    # 1 hour
"news": 21600,      # 6 hours
"quote": 86400,     # 24 hours
```

To clear cache: `rm -rf .cache/`

## Scheduling

### Option A: Cron Job (Recommended for Desktop)

```bash
crontab -e
```

Add line to run daily at 7 AM:

```cron
0 7 * * * cd /path/to/MaizNews && python3 daily_briefing_generator.py
```

With logging:

```cron
0 7 * * * cd /path/to/MaizNews && python3 daily_briefing_generator.py >> daily-briefing.log 2>&1
```

### Option B: GitHub Actions (Recommended for Cloud)

The `.github/workflows/daily-briefing.yml` workflow runs daily at 7 AM UTC.

**Setup:**

1. Push this repo to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add secret `GOOGLE_CREDENTIALS` with contents of your `credentials.json`
4. Workflow will auto-run daily and commit HTML files to repo

To manually trigger: Go to **Actions → Generate Daily Briefing → Run workflow**

### Option C: systemd Timer (Linux)

Create `~/.config/systemd/user/daily-briefing.service`:

```ini
[Unit]
Description=Generate Daily Briefing

[Service]
ExecStart=/usr/bin/python3 /path/to/MaizNews/daily_briefing_generator.py
WorkingDirectory=/path/to/MaizNews
```

Create `~/.config/systemd/user/daily-briefing.timer`:

```ini
[Unit]
Description=Daily Briefing Timer

[Timer]
OnCalendar=*-*-* 07:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable: `systemctl --user enable daily-briefing.timer`

## Email Delivery

To automatically email the generated HTML:

### Using System Mail

```bash
python3 daily_briefing_generator.py && \
mail -e -H 'Content-Type: text/html' your-email@example.com < daily-briefing-*.html
```

### Using SMTP

Add to `daily_briefing_generator.py`:

```python
import smtplib
from email.mime.text import MIMEText

def email_briefing(html_file, recipient):
    with open(html_file) as f:
        html = f.read()
    
    msg = MIMEText(html, 'html')
    msg['Subject'] = f"Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = 'sender@example.com'
    msg['To'] = recipient
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('sender@example.com', 'app-password')
        server.send_message(msg)
```

## Troubleshooting

### "credentials.json not found"

Download it from Google Cloud Console (see Setup section above).

### "No credentials available"

Delete `token.pickle` and re-run. This will prompt browser auth again:

```bash
rm token.pickle
python daily_briefing_generator.py
```

### API quota exceeded

Google APIs have free tier limits. If you hit them:
- Calendar: 1 million requests/month (per project)
- Gmail: 1 million requests/month (per project)
- Each briefing uses ~5-10 API calls

If needed, upgrade your plan in Google Cloud Console.

### Cache not working

Verify `.cache/` directory exists and is writable:

```bash
ls -la .cache/
# Should show cache files like: calendar.json, gmail.json, etc.
```

Clear cache and retry:

```bash
rm -rf .cache/
python daily_briefing_generator.py
```

## File Structure

```
MaizNews/
├── daily_briefing_generator.py    # Main script
├── cache.py                        # Caching layer
├── auth.py                        # Google OAuth2
├── calendar_client.py             # Calendar API wrapper
├── gmail_client.py                # Gmail API wrapper
├── weather_client.py              # Open-Meteo weather API
├── news_client.py                 # Google News RSS
├── quote_client.py                # Zenquotes daily quote
├── credentials.json               # Google OAuth (gitignored)
├── token.pickle                   # Auth token cache (gitignored)
├── requirements.txt               # Python dependencies
├── daily-briefing-2026-06-20.html # Generated output
└── .github/workflows/
    └── daily-briefing.yml         # GitHub Actions
```

## Data Flow

```
Google Calendar ──┐
Google Gmail ─────┤
Open-Meteo ───────┼─> daily_briefing_generator.py ──> daily-briefing-[DATE].html
Google News RSS ──┤                                     (16 KB, self-contained)
Zenquotes ────────┘
```

## Development

### Testing

Run the test generator:

```bash
python3 test_mock_html.py
```

This generates a sample HTML without requiring Google credentials.

### Code Structure

- **Rendering functions**: `render_*_section()` - Format each data source
- **Data fetching**: `fetch_all_data()` - Orchestrates all clients
- **Caching**: `cache.py` - Simple file-based cache
- **HTML generation**: `generate_html()` - Combines sections + CSS

### Customization

To add new data sources:

1. Create a client module (e.g., `twitter_client.py`)
2. Add to `fetch_all_data()` function
3. Create `render_twitter_section()` function
4. Add to `generate_html()` sections

## License & Attribution

- Calendar: Google Calendar API (requires auth)
- Email: Gmail API (requires auth)
- Weather: Open-Meteo (free, no auth)
- News: Google News RSS (free, no auth)
- Quotes: Zenquotes (free, no auth)

All styling and HTML template created custom for this project.

## Support

For issues:
1. Check `.cache/` to see what data was fetched
2. Run with verbose output: `python3 daily_briefing_generator.py`
3. Check `daily-briefing.log` if using cron
4. Verify credentials.json is valid JSON and readable

## Next Steps

1. ✅ Run it once manually
2. ✅ Verify output looks good in browser
3. ✅ Set up scheduling (cron or GitHub Actions)
4. ✅ Optional: Configure email delivery
5. ✅ Share with friends/family!
