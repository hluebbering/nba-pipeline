"""
Monkey-patch nba_api to route through RapidAPI (or ScraperAPI) &
add exponential back-off so Dagster stops bombing on timeouts.
"""
import os, backoff, requests

RAPID = os.getenv("RAPIDAPI_KEY")
SCRAPER = os.getenv("SCRAPERAPI_KEY")

def _proxied_url(url: str) -> str:
    if RAPID:
        return (
            "https://rapidapi.p.rapidapi.com/?"        # RapidAPI NBA-Stats proxy
            f"rapidapi-key={RAPID}&url={url}"
        )
    if SCRAPER:
        return f"http://api.scraperapi.com/?key={SCRAPER}&url={url}"
    return url  # fall back to direct hit


from nba_api.stats.library.http import NBAStatsHTTP
# grab whatever the base class exposes (old versions) ­– else fall back to {}
BASE_HEADERS = getattr(NBAStatsHTTP, "HEADERS", {})


class PatchedHTTP(NBAStatsHTTP):
    HEADERS = {
        **_BASE_HEADERS,
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError),
                          max_time=300)
    def send_api_request(self, endpoint: str, params: dict, **kwargs):
        url = self.BASE_URL + endpoint
        url = _proxied_url(url)
        kwargs.setdefault("timeout", 30)
        return requests.get(url, headers=self.HEADERS, params=params, **kwargs)


# ⬇️ install the monkey-patch **before** anything imports nba_api endpoints
import nba_api.stats.library.http
nba_api.stats.library.http.NBAStatsHTTP = PatchedHTTP
