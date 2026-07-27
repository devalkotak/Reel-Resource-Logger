# Reel Resource Logger

Share Instagram reel via native share sheet -> auto-extract resource/tool/link mentioned -> log categorized into Notion.

## Architecture

- **Ingestion:** Telegram bot (IG share sheet supports Telegram natively, no OAuth). Catches forwarded video file directly, or plain link (yt-dlp/instaloader fallback if IG blocks link-only downloads).
- **Extraction:** Gemini API (gemini-1.5-flash, free tier) — send video directly, model watches + transcribes audio, no manual frame/audio extraction. Structured JSON output: title, category, tags, link, summary, price, confidence.
- **Storage:** Notion API (integration token scoped to shared pages only).
- **Hosting:** Railway free tier (500 hrs/month) — chosen over Render (cold-starts) and Cloudflare Workers (video/timeout size limits).

## Notion DB

"Reel Resources" — https://app.notion.com/p/f70aec465b124cdb92360238819e6230
Data source ID: `2d6fb477-9d83-48c1-98b5-85e83964e283`

Schema:
- Title (title)
- Category (select, fixed): Tool / App, Website / Platform, Product, Book / Course, Article / Guide, Recipe, Place / Travel, Service, Other
- Domain Tags (multi-select, expandable): AI, Productivity, Fitness, Design, Finance, Travel, Cooking, Fashion, Tech, Marketing
- Resource Link (url)
- Source Reel (url)
- Summary (text)
- Creator Handle (text)
- Date Added (date)
- Status (select): New, Reviewed, Tried, Archived
- Price (select): Free, Paid, Freemium, Unknown
- Confidence (select): High, Low — flags reels where Gemini is unsure of link extraction

## Status

- [x] Notion DB created + schema defined
- [x] Code: bot.py, extract.py, notion_push.py, downloader.py (yt-dlp link fallback)
- [x] Bug pass: Notion API version pin, blocking-call fix (asyncio.to_thread), Gemini poll backoff, yt-dlp output-path fix
- [x] Caption capture (yt-dlp description + Telegram caption) fed into Gemini as extra context
- [x] Guaranteed cleanup of all downloaded video/fragment files after each run
- [x] SETUP.md written — step-by-step key/token guide (Telegram, Gemini, Notion, Railway)
- [ ] Telegram bot token (BotFather)
- [ ] Gemini API key
- [ ] Notion integration token + share DB page with integration
- [ ] Railway account setup
- [ ] Runtime test (nothing has executed yet — code is unverified against real APIs)

## Files

- `bot.py` — Telegram handler (video or link in, routes to shared `process_video`)
- `downloader.py` — yt-dlp fallback to pull video + caption from a plain IG link, plus cleanup helper
- `extract.py` — Gemini call + JSON extraction prompt (caption-aware)
- `notion_push.py` — maps extracted JSON to Notion page props, pushes via API
- `requirements.txt`
- `railway.json` / `Procfile`
- `.env.example` — required env vars (no real secrets committed)
- `SETUP.md` — key/token setup walkthrough

## Next session

Pick up at: get the 3 keys via SETUP.md (Telegram, Gemini, Notion), fill `.env`, run `python bot.py` locally, forward a real reel, verify a row lands in Notion. Then deploy to Railway.
