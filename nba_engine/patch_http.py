# scraper.py  (or inside your Dagster asset)
import os, urllib.parse, requests, time, random

SA_KEY = os.environ["SCRAPERAPI_KEY"]          # premium key
NBA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://stats.nba.com",
    "Origin":  "https://www.nba.com",
    "x-nba-stats-token":  "true",
    "x-nba-stats-origin": "stats",
}

def scrape_nba(endpoint: str, params: dict, retries: int = 3) -> dict:
    """Call stats.nba.com via ScraperAPI-premium + header-forwarding."""
    nba_url = f"https://stats.nba.com/stats/{endpoint}?{urllib.parse.urlencode(params)}"

    proxy_params = {
        "api_key": SA_KEY,
        "premium": "true",
        "keep_headers": "true",
        "country_code": "eu",          # EU exit works; switch / randomize if needed
        "retry":        "3",
        "timeout":      "90000",       # ms
        "url": nba_url,
    }
    url = "https://api.scraperapi.com?" + urllib.parse.urlencode(proxy_params, safe=":/?&=")

    last_exc = None
    for _ in range(retries):
        try:
            r = requests.get(url, headers=NBA_HEADERS, timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code in {403, 504, 429, 500}:
                # throw to retry; let ScraperAPI rotate proxy
                raise RuntimeError(f"ScraperAPI {r.status_code}")
        except Exception as exc:
            last_exc = exc
            time.sleep(random.uniform(1.1, 2.5))   # jitter to dodge ban waves
    raise last_exc or RuntimeError("Unreachable")
