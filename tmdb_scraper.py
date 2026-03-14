import requests
import time
import json

# --- CONFIG ---
TMDB_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkNWQ2MDI0YjMxODkzYzEyNThkZmMyZGJhNzgzNWMwNCIsIm5iZiI6MTc3MzQ4NDIxNy43Miwic3ViIjoiNjliNTM4YjkzMDBkN2NhMDZjNjczMDIyIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.DwZwiDn2BRZJgYCYCjGkUBNNIhlzcgqm-F6WAzr3f_M"  # Replace with your TMDB API key
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

HEADERS = {"Authorization": f"Bearer {TMDB_API_KEY}"}

# Helper to fetch most recent items for a provider
def fetch_recent(provider_id, media_type, count=20):
    results = []
    page = 1
    while len(results) < count:
        url = f"{BASE_URL}/discover/{media_type}"
        params = {
            "with_watch_providers": provider_id,
            "watch_region": "US",
            "sort_by": "release_date.desc" if media_type == "movie" else "first_air_date.desc",
            "page": page,
            "language": "en-US",
            "include_adult": False,
            "with_release_type": "3|2" if media_type == "movie" else None  # Streaming/VOD
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        resp = requests.get(url, params=params, headers={"accept": "application/json", "Authorization": f"Bearer {TMDB_API_KEY}"})
        data = resp.json()
        items = data.get("results", [])
        if not items:
            break
        results.extend(items)
        page += 1
        time.sleep(0.2)  # Be nice to the API
    return results[:count]

output = {}
for provider, pid in PROVIDERS.items():
    print(f"Fetching for {provider}...")
    movies = fetch_recent(pid, "movie", 20)
    series = fetch_recent(pid, "tv", 20)
    output[provider] = {
        "movies": movies,
        "series": series
    }

with open("tmdb_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Done! Data saved to tmdb_data.json")
