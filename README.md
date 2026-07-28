# Reel Resource Logger

Share Instagram reel via native share sheet -> auto-extract resource/tool/link mentioned -> log categorized into Notion.

## Architecture

- **Ingestion:** Telegram bot (IG share sheet supports Telegram natively, no OAuth). Catches forwarded video file directly, or plain link (yt-dlp/instaloader fallback if IG blocks link-only downloads).
- **Extraction:** Gemini API via `google-genai` SDK (model: `gemini-flash-latest`) — send video directly, model watches + transcribes audio, no manual frame/audio extraction. Returns a JSON array (one reel can name multiple resources), each with: title, category, tags, link, summary, price, confidence. Model infers the real URL from a spoken/shown name when no domain is given (marked confidence "Low" when inferred).
- **Storage:** Notion API (integration token scoped to shared pages only).
- **Hosting:** Railway free tier (500 hrs/month) — chosen over Render (cold-starts) and Cloudflare Workers (video/timeout size limits).

## Notion DB

"Reel Resources" — https://app.notion.com/p/f70aec465b124cdb92360238819e6230
Data source ID: `2d6fb477-9d83-48c1-98b5-85e83964e283`

Schema:
- Title (title)
- Category (select, fixed): Tool / App, Website / Platform, Product, Book / Course, Article / Guide, Recipe, Place / Travel, Service, Other
- Domain Tags (multi-select, open-ended): model chooses 1-4 specific tags per resource, no fixed taxonomy — Notion auto-creates new options as they appear
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
- [x] All 3 keys obtained, `.env` filled, bot run locally end-to-end against real APIs
- [x] Fixed: `load_dotenv()` import order, yt-dlp version bump
- [x] Migrated Gemini calls from deprecated `google-generativeai` to `google-genai` SDK (new AQ-format API keys aren't accepted by the old SDK's auth path)
- [x] Fixed model name churn (`gemini-1.5-flash` retired -> `gemini-2.5-flash` new-project-restricted -> settled on `gemini-flash-latest`)
- [x] Open-ended Domain Tags (model picks freely, no fixed list)
- [x] Prompt hardened: model must watch/listen for name even if no explicit URL is spoken, and infer the real site URL from the name using its own knowledge when no domain is given
- [x] Multi-resource support: one reel can yield multiple resources, each becomes its own Notion page
- [ ] Railway deploy
- [ ] Verify inferred-link accuracy on a real batch of reels (spot-check a few Notion rows)

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

Local end-to-end run confirmed working (Telegram -> download -> Gemini -> Notion). Pick up at: spot-check a batch of real reels for inferred-link accuracy, then deploy to Railway.
