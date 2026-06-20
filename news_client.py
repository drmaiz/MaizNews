import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

# Google News topic feeds (US English)
RSS_FEEDS = {
    "Breaking": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "Global": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
    "Markets": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
    "Tech & AI": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
    "Politics": "https://news.google.com/rss/search?q=US+politics&hl=en-US&gl=US&ceid=US:en",
    "Global Health": "https://news.google.com/rss/search?q=global+health+WHO+CDC&hl=en-US&gl=US&ceid=US:en",
    "Science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US&ceid=US:en",
}

USER_AGENT = {"User-Agent": "Mozilla/5.0 (MaizNews Daily Briefing)"}


def _clean_title(title: str) -> str:
    """Google News titles often include ' - Source'. Remove trailing source suffix when present."""
    if not title:
        return ""
    if " - " in title:
        return title.rsplit(" - ", 1)[0].strip()
    return title.strip()


def _clean_description(desc: str) -> str:
    """Normalize RSS description text for concise rendering."""
    if not desc:
        return ""
    # Keep lightweight cleanup only; generator will truncate further as needed
    return " ".join(desc.replace("\n", " ").split()).strip()


def _parse_time(published_text: str):
    """Parse RFC2822 publish time safely."""
    if not published_text:
        return None
    try:
        return parsedate_to_datetime(published_text)
    except Exception:
        return None


def _fetch_feed(category: str, url: str, per_feed_limit: int = 6):
    """Fetch and parse one RSS feed into normalized article dicts."""
    articles = []

    resp = requests.get(url, timeout=10, headers=USER_AGENT)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    items = root.findall(".//item")[:per_feed_limit]

    for item in items:
        raw_title = item.findtext("title", "")
        title = _clean_title(raw_title)
        source = item.findtext("source", "") or "Unknown"
        description = _clean_description(item.findtext("description", ""))
        link = item.findtext("link", "")
        published_text = item.findtext("pubDate", "")
        published_dt = _parse_time(published_text)

        if not title:
            continue

        articles.append(
            {
                "title": title,
                "source": source,
                "description": description,
                "summary": description,
                "url": link,
                "category": category,
                "published_at": published_dt.isoformat() if published_dt else "",
                "_published_dt": published_dt,
            }
        )

    return articles


def _dedupe_articles(articles):
    """Deduplicate by normalized title."""
    seen = set()
    out = []
    for a in articles:
        key = a.get("title", "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


def _select_balanced(articles, max_results):
    """
    Build a category-balanced list.

    Goals:
    - ensure non-medical breadth
    - avoid overrepresentation from one category
    - keep freshest items first when possible
    """
    if not articles:
        return []

    # Freshest first when timestamp exists
    articles = sorted(
        articles,
        key=lambda x: (x.get("_published_dt") is not None, x.get("_published_dt")),
        reverse=True,
    )

    preferred_order = [
        "Breaking",
        "Markets",
        "Tech & AI",
        "Politics",
        "Global",
        "Science",
        "Global Health",
    ]

    by_category = {cat: [] for cat in preferred_order}
    for a in articles:
        cat = a.get("category") or "Breaking"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(a)

    selected = []
    used_titles = set()

    # Pass 1: one from each key category (health last)
    for cat in preferred_order:
        if len(selected) >= max_results:
            break
        if by_category.get(cat):
            candidate = by_category[cat][0]
            t = candidate["title"].strip().lower()
            if t not in used_titles:
                selected.append(candidate)
                used_titles.add(t)

    # Pass 2: fill remaining slots with freshest stories,
    # but cap Global Health at 2 items by default.
    health_count = sum(1 for x in selected if x.get("category") == "Global Health")
    for a in articles:
        if len(selected) >= max_results:
            break
        t = a["title"].strip().lower()
        if t in used_titles:
            continue
        if a.get("category") == "Global Health" and health_count >= 2:
            continue
        selected.append(a)
        used_titles.add(t)
        if a.get("category") == "Global Health":
            health_count += 1

    # Strip internal sort key before returning
    for a in selected:
        a.pop("_published_dt", None)

    return selected[:max_results]


def get_headlines(max_results=7):
    """
    Return balanced news headlines with richer metadata.

    Output schema per item:
    - title
    - source
    - description / summary
    - url
    - category
    - published_at (ISO string when available)
    """
    all_articles = []

    try:
        for category, feed_url in RSS_FEEDS.items():
            try:
                all_articles.extend(_fetch_feed(category, feed_url, per_feed_limit=5))
            except Exception:
                # Continue on individual feed failure for resilience
                continue

        deduped = _dedupe_articles(all_articles)
        return _select_balanced(deduped, max_results=max_results)

    except Exception:
        return []
