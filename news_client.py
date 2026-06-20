import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

USER_AGENT = {"User-Agent": "Mozilla/5.0 (MaizNews Daily Briefing)"}

# Source strategy aligned to daily-briefing-auto-fetch.md
# Mix of direct trusted outlets + Google News publisher/topic search fallbacks.
FEEDS = {
    "Breaking": [
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",  # q injected
    ],
    "Global": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
    ],
    "Markets": [
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
    ],
    "Tech & AI": [
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
    ],
    "Politics": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
    ],
    "Global Health": [
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
    ],
    "Science": [
        "https://www.theguardian.com/science/rss",
        "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
    ],
}

# Publisher/topic queries that bias toward your preferred outlets.
CATEGORY_QUERIES = {
    "Breaking": "(Reuters OR AP OR BBC OR NPR OR Guardian) breaking world",
    "Global": "(Reuters OR AP OR BBC OR Guardian OR NPR OR FT) world diplomacy",
    "Markets": "(Bloomberg OR CNBC OR WSJ OR FT OR Reuters) markets inflation oil economy",
    "Tech & AI": "(MIT Technology Review OR The Verge OR Ars Technica OR Reuters) AI technology",
    "Politics": "(Reuters OR AP OR NPR OR BBC OR Guardian) US politics congress policy",
    "Global Health": "(WHO OR CDC OR Reuters OR AP OR BBC) outbreak public health",
    "Science": "(Nature OR Science OR Reuters OR BBC OR Guardian) research discovery",
}

TRUSTED_SOURCE_HINTS = [
    "reuters",
    "associated press",
    "ap",
    "bbc",
    "npr",
    "guardian",
    "wall street journal",
    "wsj",
    "financial times",
    "ft",
    "bloomberg",
    "cnbc",
    "ars technica",
    "technology review",
    "the verge",
    "who",
    "cdc",
]


def _clean_title(title: str) -> str:
    if not title:
        return ""
    # Google News sometimes appends source with a hyphen suffix
    if " - " in title:
        return title.rsplit(" - ", 1)[0].strip()
    return " ".join(title.split()).strip()


def _clean_description(desc: str) -> str:
    if not desc:
        return ""
    # lightweight normalization; renderer handles final truncation
    return " ".join(desc.replace("\n", " ").replace("\r", " ").split()).strip()


def _parse_time(published_text: str):
    if not published_text:
        return None
    try:
        return parsedate_to_datetime(published_text)
    except Exception:
        return None


def _source_from_item(item) -> str:
    # RSS source tag
    source = item.findtext("source", "")
    if source:
        return source.strip()

    # dc:creator fallback
    creator = item.findtext("{http://purl.org/dc/elements/1.1/}creator", "")
    if creator:
        return creator.strip()

    return "Unknown"


def _is_trusted_source(source: str, title: str = "") -> bool:
    text = f"{source} {title}".lower()
    return any(hint in text for hint in TRUSTED_SOURCE_HINTS)


def _build_feed_url(template: str, query: str) -> str:
    if "{q}" in template:
        return template.format(q=quote_plus(query))
    return template


def _fetch_feed(url: str, category: str, per_feed_limit: int = 6):
    articles = []

    resp = requests.get(url, timeout=10, headers=USER_AGENT)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    items = root.findall(".//item")[:per_feed_limit]

    for item in items:
        title = _clean_title(item.findtext("title", ""))
        if not title:
            continue

        source = _source_from_item(item)
        description = _clean_description(item.findtext("description", ""))
        link = item.findtext("link", "")

        published_text = (
            item.findtext("pubDate", "")
            or item.findtext("published", "")
            or item.findtext("updated", "")
        )
        published_dt = _parse_time(published_text)

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
                "_trusted": _is_trusted_source(source, title),
            }
        )

    return articles


def _dedupe_articles(articles):
    seen = set()
    out = []
    for a in articles:
        key = a.get("title", "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


def _sort_articles(articles):
    # Trusted + freshest first
    return sorted(
        articles,
        key=lambda x: (
            1 if x.get("_trusted") else 0,
            1 if x.get("_published_dt") is not None else 0,
            x.get("_published_dt"),
        ),
        reverse=True,
    )


def _select_balanced(articles, max_results):
    if not articles:
        return []

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
    for a in _sort_articles(articles):
        cat = a.get("category") or "Breaking"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(a)

    selected = []
    used = set()

    # Pass 1: one per category in priority order
    for cat in preferred_order:
        if len(selected) >= max_results:
            break
        for cand in by_category.get(cat, []):
            t = cand["title"].strip().lower()
            if t in used:
                continue
            selected.append(cand)
            used.add(t)
            break

    # Pass 2: fill remaining from all categories, cap medical-heavy output
    health_count = sum(1 for x in selected if x.get("category") == "Global Health")
    for a in _sort_articles(articles):
        if len(selected) >= max_results:
            break
        t = a["title"].strip().lower()
        if t in used:
            continue
        if a.get("category") == "Global Health" and health_count >= 2:
            continue
        selected.append(a)
        used.add(t)
        if a.get("category") == "Global Health":
            health_count += 1

    for a in selected:
        a.pop("_published_dt", None)
        a.pop("_trusted", None)

    return selected[:max_results]


def get_headlines(max_results=7):
    """
    Return a balanced set of stories across trusted-source categories.

    Output fields expected by daily_briefing_generator:
    - title
    - source
    - description / summary
    - url
    - category
    - published_at
    """
    all_articles = []

    try:
        for category, feed_templates in FEEDS.items():
            query = CATEGORY_QUERIES.get(category, "top news")
            for template in feed_templates:
                url = _build_feed_url(template, query)
                try:
                    all_articles.extend(_fetch_feed(url, category, per_feed_limit=5))
                except Exception:
                    # Continue on feed failures for resiliency
                    continue

        deduped = _dedupe_articles(all_articles)
        return _select_balanced(deduped, max_results=max_results)

    except Exception:
        return []
