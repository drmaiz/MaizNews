import requests
import xml.etree.ElementTree as ET

RSS_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"


def get_headlines(max_results=5):
    try:
        resp = requests.get(RSS_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        headlines = []
        for item in root.findall(".//item")[:max_results]:
            title = item.findtext("title", "")
            source = item.findtext("source", "")
            # Google News titles come as "Headline - Source Name", strip the source suffix
            if " - " in title:
                title = title.rsplit(" - ", 1)[0].strip()
            headlines.append({"title": title, "source": source})
        return headlines
    except Exception:
        return []
