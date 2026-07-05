"""
Fetch trending pearl / pearl-jewelry YouTube videos and write them to data.json.

Requires an environment variable YT_API_KEY containing a YouTube Data API v3 key.
Get one free at https://console.cloud.google.com/ (enable "YouTube Data API v3",
then create an API key under Credentials). The free daily quota (10,000 units)
is far more than this script needs.

Run locally:
    export YT_API_KEY="your-key-here"
    pip install -r requirements.txt
    python fetch_youtube_data.py
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

API_KEY = os.environ.get("YT_API_KEY")
if not API_KEY:
    print("ERROR: Set the YT_API_KEY environment variable first.", file=sys.stderr)
    sys.exit(1)

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# Search terms covering the pearl jewelry niche. Edit this list to widen/narrow scope.
QUERIES = [
    "pearl jewelry",
    "pearl necklace",
    "pearl earrings",
    "pearl bracelet",
    "pearl ring",
    "freshwater pearl jewelry",
    "akoya pearl",
    "tahitian pearl jewelry",
    "pearl jewelry trends 2026",
    "how to style pearls",
]

# Category keywords used to tag/filter videos on the dashboard.
CATEGORY_KEYWORDS = {
    "Necklaces": ["necklace", "strand", "choker"],
    "Earrings": ["earring", "stud", "hoop"],
    "Rings": ["ring"],
    "Bracelets": ["bracelet", "bangle"],
    "Styling & Trends": ["style", "trend", "how to", "outfit", "look"],
}


def categorize(title: str) -> str:
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            return category
    return "Other"


def search_video_ids(query: str, max_results: int = 15) -> list:
    params = {
        "key": API_KEY,
        "part": "id",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results,
        "relevanceLanguage": "en",
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    return [item["id"]["videoId"] for item in resp.json().get("items", [])]


def fetch_video_details(video_ids: list) -> list:
    """YouTube's videos.list endpoint accepts up to 50 IDs per call."""
    details = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        params = {
            "key": API_KEY,
            "part": "snippet,statistics",
            "id": ",".join(chunk),
        }
        resp = requests.get(VIDEOS_URL, params=params, timeout=30)
        resp.raise_for_status()
        details.extend(resp.json().get("items", []))
    return details


def main():
    all_ids = set()
    for query in QUERIES:
        try:
            ids = search_video_ids(query)
            all_ids.update(ids)
        except requests.HTTPError as e:
            print(f"Search failed for '{query}': {e}", file=sys.stderr)

    print(f"Collected {len(all_ids)} unique video IDs, fetching details...")
    raw_videos = fetch_video_details(list(all_ids))

    videos = []
    for item in raw_videos:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        video_id = item["id"]
        title = snippet.get("title", "Untitled")

        published_at = snippet.get("publishedAt")
        views = int(stats.get("viewCount", 0))

        # Rough "velocity" score: views per day since publish, so brand-new
        # viral videos don't get buried under old high-view-count uploads.
        velocity = views
        if published_at:
            try:
                published_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                days_live = max((datetime.now(timezone.utc) - published_dt).days, 1)
                velocity = round(views / days_live, 1)
            except ValueError:
                pass

        videos.append(
            {
                "id": video_id,
                "title": title,
                "channel": snippet.get("channelTitle", "Unknown channel"),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url")
                or snippet.get("thumbnails", {}).get("default", {}).get("url"),
                "publishedAt": published_at,
                "views": views,
                "likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                "comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
                "velocity": velocity,
                "category": categorize(title),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )

    # Sort by raw views, descending, and keep a healthy top slice.
    videos.sort(key=lambda v: v["views"], reverse=True)
    videos = videos[:60]

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "videoCount": len(videos),
        "videos": videos,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(videos)} videos to data.json")


if __name__ == "__main__":
    main()
