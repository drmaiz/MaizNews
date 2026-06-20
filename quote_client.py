import requests


def get_quote():
    try:
        resp = requests.get("https://zenquotes.io/api/today", timeout=10)
        resp.raise_for_status()
        data = resp.json()[0]
        return {"text": data["q"], "author": data["a"]}
    except Exception:
        return {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"}
