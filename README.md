# Nacre — Pearl Jewelry Trends Dashboard

A dashboard of the most-watched pearl-jewelry YouTube videos, refreshed automatically
once a day, hosted for free on GitHub Pages.

## How it works

```
GitHub Actions (daily cron)
        │
        ▼
fetch_youtube_data.py  ──calls──▶  YouTube Data API v3
        │
        ▼
   data.json  (committed back to the repo)
        │
        ▼
   index.html (GitHub Pages)  ──reads──▶  data.json
```

Every day, a free GitHub Actions job runs the Python script, which searches
YouTube for pearl-jewelry related terms, ranks the results by views, and saves
them to `data.json`. The dashboard (`index.html`) is a static page that reads
that file and renders it — no server needed.

## One-time setup (about 10 minutes)

### 1. Get a free YouTube Data API key
1. Go to [console.cloud.google.com](https://console.cloud.google.com/) and create a project (or use an existing one).
2. In the search bar, find **"YouTube Data API v3"** and click **Enable**.
3. Go to **APIs & Services → Credentials → Create Credentials → API key**.
4. Copy the key. (Optional but recommended: click "Restrict key" and limit it to the YouTube Data API v3.)

### 2. Create a GitHub repository
1. Create a new **public** repo (public is required for free GitHub Pages).
2. Upload all the files from this folder (`fetch_youtube_data.py`, `requirements.txt`, `index.html`, `data.json`, `.github/workflows/update-data.yml`) — or `git push` them if you're using the command line.

### 3. Add your API key as a secret
1. In your repo, go to **Settings → Secrets and variables → Actions → New repository secret**.
2. Name it `YT_API_KEY` and paste your API key as the value.

### 4. Turn on GitHub Pages
1. Go to **Settings → Pages**.
2. Under "Build and deployment", set **Source** to "Deploy from a branch".
3. Choose the `main` branch and the `/ (root)` folder, then save.
4. GitHub will give you a free URL, typically:
   `https://<your-username>.github.io/<repo-name>/`
   That link is your live dashboard — bookmark it, and it will update itself every day.

### 5. (Optional) Run it once manually to get real data right away
1. Go to the **Actions** tab in your repo.
2. Click on **"Update pearl jewelry trends data"** in the left sidebar.
3. Click **Run workflow** → **Run workflow**.
4. Wait ~30 seconds, refresh your Pages URL, and you'll see live data instead of the sample set.

## Customizing

- **Search terms**: edit the `QUERIES` list near the top of `fetch_youtube_data.py` to widen or narrow what counts as "pearl jewelry."
- **Refresh time**: edit the `cron` line in `.github/workflows/update-data.yml` (times are in UTC).
- **Categories**: edit `CATEGORY_KEYWORDS` in `fetch_youtube_data.py` to change how videos get tagged as Necklaces / Earrings / etc.
- **Look and feel**: all styling lives in the `<style>` block of `index.html` — colors are defined once at the top as CSS variables (`--gold`, `--sheen`, etc.) so they're easy to swap.

## About the "free domain" part

GitHub Pages gives you a free `github.io` subdomain automatically — no separate
domain purchase needed. If you'd like a custom domain later (e.g.
`pearltrends.com`), you can buy one from any registrar and point it at your
GitHub Pages site under **Settings → Pages → Custom domain** — but that step is
optional and costs money, whereas everything above is completely free.

## API quota note

The free YouTube Data API quota is 10,000 units/day. Each search call costs
100 units; with 10 search terms per run, that's ~1,000 units/day — well within
the free tier, even if you trigger a manual run in addition to the daily one.
