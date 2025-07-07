"""
Monkey-patch nba_api so every request is wrapped by ScraperAPI.
Import this at package init *before* any endpoint call.
"""
import os, urllib.parse as up
from nba_api.library.http import NBAStatsHTTP

class ProxiedHTTP(NBAStatsHTTP):
    def send_api_request(self, endpoint, params, **kwargs):
        # build the normal stats.nba.com URL first
        base = self.NBA_STATS_BASE_URL + endpoint
        url   = f"{base}?{up.urlencode(params, doseq=True)}"

        # wrap with ScraperAPI
        key   = os.getenv("SCRAPERAPI_KEY")
        proxy = (
            "https://api.scraperapi.com/"
            f"?api_key={key}&country_code=us&url={up.quote_plus(url)}"
        )
        return self.get_session().get(proxy, timeout=self.timeout)

# hot-swap the class used by nba_api
import nba_api.library.http as _http
_http.NBAStatsHTTP = ProxiedHTTP
