import requests
import time
import json
import os

# --- CONFIG ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY environment variable is not set")
BASE_URL = "https://api.themoviedb.org/3"

# Provider mapping: {Display Name: TMDB Provider ID}
PROVIDERS = {
    "AppleTV": 350,
    "HBO Max": 1899,
    "Netflix": 8,
    "Paramount": 531,
    "Hulu": 15,
    "Prime": 9,
    "Disney": 337
}

# Genre IDs to exclude: Animation (16), Family (10751), Kids/TV Kids (10762)
EXCLUDED_GENRES = "16,10751,10762"

def fetch_discover(provider_id, media_type, sort_by, count=20, extra_params=None):
    results = []
    page = 1
    while len(results) < count:
        params = {
            "with_watch_providers": provider_id,
            "watch_region": "US",
            "sort_by": sort_by,
            "page": page,
            "language": "en-US",
            "include_adult": False,
            "without_genres": EXCLUDED_GENRES,
            "with_release_type": "3|2" if media_type == "movie" else None
        }
        if extra_params:
            params.update(extra_params)
        params = {k: v for k, v in params.items() if v is not None}
        resp = requests.get(
            f"{BASE_URL}/discover/{media_type}",
            params=params,
            headers={"accept": "application/json", "Authorization": f"Bearer {TMDB_API_KEY}"}
        )
        data = resp.json()
        items = data.get("results", [])
        if not items:
            break
        results.extend(items)
        page += 1
        time.sleep(0.2)
    return results[:count]

def fetch_latest(provider_id, media_type, count=20):
    sort_by = "release_date.desc" if media_type == "movie" else "first_air_date.desc"
    return fetch_discover(provider_id, media_type, sort_by, count)

def fetch_top_rated(provider_id, media_type, count=20):
    min_votes = 50 if media_type == "movie" else 20
    return fetch_discover(provider_id, media_type, "vote_average.desc", count,
                          extra_params={"vote_count.gte": min_votes})

output = {}
for provider, pid in PROVIDERS.items():
    print(f"Fetching for {provider}...")
    output[provider] = {
        "movies_latest":    fetch_latest(pid, "movie", 20),
        "movies_top":       fetch_top_rated(pid, "movie", 20),
        "series_latest":    fetch_latest(pid, "tv", 20),
        "series_top":       fetch_top_rated(pid, "tv", 20),
    }

with open("tmdb_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Done! Data saved to tmdb_data.json")
