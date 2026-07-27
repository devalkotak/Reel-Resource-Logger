# Setup Guide: Keys and Tokens

Four things needed before this bot runs. Fill values into `.env` (copy from `.env.example`).

## 1. Telegram Bot Token

1. Open Telegram, search **@BotFather**.
2. Send `/newbot`.
3. Give it a name (display name) and a username (must end in `bot`, e.g. `reel_logger_bot`).
4. BotFather replies with a token like `123456789:AAH...`. Copy it.
5. Set in `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456789:AAH...
   ```

**Getting reels to it:** On Instagram, tap Share on a reel -> select Telegram -> pick this bot's chat. Or forward the video from a chat where you saved it.

## 2. Gemini API Key

1. Go to https://aistudio.google.com/apikey
2. Sign in with Google account, click **Create API key**.
3. Choose a Google Cloud project (or let it create one) — free tier is fine for gemini-1.5-flash.
4. Copy the key.
5. Set in `.env`:
   ```
   GEMINI_API_KEY=AIza...
   ```

Free tier limits (check current quota at https://ai.google.dev/gemini-api/docs/rate-limits) — fine for personal reel-logging volume.

## 3. Notion Integration Token

1. Go to https://www.notion.so/my-integrations
2. Click **New integration**.
3. Name it (e.g. "Reel Resource Logger"), select the workspace, Internal integration type.
4. Under Capabilities, make sure **Read content**, **Insert content**, **Update content** are checked.
5. Click **Submit**, copy the **Internal Integration Secret** (starts `ntn_` or `secret_`).
6. Set in `.env`:
   ```
   NOTION_TOKEN=ntn_...
   ```
7. **Share the DB with the integration** — open the "Reel Resources" database in Notion, click `•••` (top right) -> **Connections** -> **Connect to** -> select your integration. Without this step the API calls 404.

`NOTION_DATA_SOURCE_ID` is already set in `.env.example` (`2d6fb477-9d83-48c1-98b5-85e83964e283`) — no action needed unless the DB is recreated.

## 4. Local test run

```
pip install -r requirements.txt
cp .env.example .env   # then fill in the 3 keys above
python bot.py
```

Forward a reel to the bot in Telegram, watch the console log, check the Notion DB for a new row.

## 5. Railway deploy (once local test passes)

1. https://railway.app -> New Project -> Deploy from GitHub repo -> select `Reel-Resource-Logger`.
2. In the Railway project's **Variables** tab, add the same 4 keys from `.env`.
3. Railway picks up `railway.json` / `Procfile` automatically (`worker: python bot.py`).
4. Deploy — bot runs continuously via polling, no public URL needed.
