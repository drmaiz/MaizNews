# MCP Integration for Daily Briefing Generator

This document describes the integration of Gmail and Google Calendar MCP connectors with the Daily Briefing Generator.

## Overview

The Daily Briefing Generator now supports two modes for accessing Gmail and Google Calendar data:

1. **MCP Mode (Recommended)** - Uses MCP connectors available in Claude Code environments
2. **Legacy Mode** - Uses Google API client library with OAuth2 credentials

## Architecture

### New Components

#### `mcp_client.py`
Provides wrapper classes for MCP connectors:
- `MCPClient` - Base client for calling MCP tools
- `MCPGmailClient` - Wraps Gmail MCP tools
- `MCPCalendarClient` - Wraps Google Calendar MCP tools

#### Updated Components

**`daily_briefing_generator.py`**
- Imported MCP clients
- Updated `fetch_all_data()` to accept `use_mcp` parameter
- Updated `main()` to accept `use_mcp` parameter (defaults to `True`)
- Maintains backward compatibility with legacy mode

**`gmail_client.py`**
- Added `get_unread_count_sync()` function
- Updated `get_recent_unread()` to work with MCP client
- Removed legacy Google API dependencies

**`calendar_client.py`**
- Updated `get_events()` to work with MCP client
- Improved ISO 8601 datetime parsing for MCP responses

## Usage

### Using MCP Connectors (Default)

```python
#!/usr/bin/env python3
from daily_briefing_generator import main

# Generate briefing using MCP connectors
filename = main(use_mcp=True)
print(f"Briefing saved to {filename}")
```

### Using Legacy Google API

```python
#!/usr/bin/env python3
from daily_briefing_generator import main

# Generate briefing using Google API (requires credentials.json)
filename = main(use_mcp=False)
print(f"Briefing saved to {filename}")
```

### Command Line

```bash
# Generate with MCP (default)
python3 daily_briefing_generator.py

# Generate with legacy API
python3 daily_briefing_generator.py --legacy
```

## Available MCP Tools

### Gmail Tools
- `mcp__Gmail__search_threads` - Search email threads
- `mcp__Gmail__get_thread` - Get thread details
- `mcp__Gmail__list_labels` - List email labels
- `mcp__Gmail__search_threads` - Advanced search

### Google Calendar Tools
- `mcp__Google-Calendar__list_events` - List calendar events
- `mcp__Google-Calendar__create_event` - Create new event
- `mcp__Google-Calendar__update_event` - Update event
- `mcp__Google-Calendar__delete_event` - Delete event

## Data Structure

### Calendar Events
```python
{
    "summary": "Event Title",
    "start": datetime,
    "end": datetime,
    "all_day": bool,
    "location": "Location"
}
```

### Email Messages
```python
{
    "subject": "Email Subject",
    "from": "sender@example.com",
    "date": datetime,
    "snippet": "Preview text..."
}
```

## Caching

Both MCP and legacy modes use the same caching system:
- Cache expires: configurable in `cache.py`
- Cache location: `.cache/` directory
- Cache keys: `calendar`, `gmail`, `weather`, `news`, `quote`

## Error Handling

The system gracefully handles MCP connection failures:
- If MCP tools are unavailable, returns empty data structures
- Continues generating briefing with available data
- Falls back to cached data when available
- Logs errors without stopping execution

## Generated Output

Generates a professional HTML briefing containing:
- **Calendar** - Next 7 days of events
- **Email** - Unread message count and recent emails
- **Weather** - Current conditions with temperature and humidity
- **News** - Top 7 headlines with sources
- **Quote** - Daily inspirational quote

## Styling

The generated HTML includes:
- Responsive design (mobile-friendly)
- Dark mode support via `prefers-color-scheme`
- Print-friendly styling
- Elegant newspaper-style layout
- Playfair Display and Inter fonts

## Example Output

The generator creates an HTML file named `daily-briefing-YYYY-MM-DD.html` with:
- Professional masthead with date and time
- Section navigation ribbon
- News items with categories and sources
- Callout boxes for key takeaways
- Footer with edition information

## Configuration

### Environment Variables
None required for MCP mode (authentication handled by Claude Code)

### Configuration Files
- `cache.py` - Caching settings
- `weather_client.py` - Weather API configuration
- `news_client.py` - News API configuration

## Troubleshooting

### No Calendar/Email Data
- MCP connectors may not be available in current environment
- Check logs for "Error getting calendar events" messages
- Use `--legacy` mode if MCP is unavailable

### Cache Issues
- Clear cache: `rm -rf .cache/`
- Disable cache: Set `CACHE_ENABLED=false` environment variable

### Missing Dependencies
- Install weather/news clients: `pip install -r requirements.txt`
- For legacy mode: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`

## Future Enhancements

- [ ] Real-time calendar sync
- [ ] Email attachment handling
- [ ] Multiple calendar support
- [ ] Custom sections
- [ ] Email templates
- [ ] Scheduled generation
- [ ] Export to PDF
- [ ] Send via email

## Contributing

To extend MCP integration:

1. Add new tool wrapper to `mcp_client.py`
2. Update relevant client files
3. Add caching support in `cache.py`
4. Update documentation
5. Test with both MCP and legacy modes

## License

Same as MaizNews project
