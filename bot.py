import asyncio
import logging
import os
import tempfile

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from downloader import download_reel
from extract import extract_from_video
from notion_push import push_resource

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def process_video(update: Update, video_path: str, source_url: str) -> None:
    try:
        extracted = await asyncio.to_thread(extract_from_video, video_path)
        await asyncio.to_thread(
            push_resource, extracted, source_reel_url=source_url, creator_handle=""
        )
        await update.message.reply_text(
            f"Logged: {extracted['title']} ({extracted['category']}, "
            f"confidence: {extracted['confidence']})"
        )
    except Exception as exc:
        logger.exception("Failed to process video")
        await update.message.reply_text(f"Failed to process: {exc}")
    finally:
        os.remove(video_path)


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video = update.message.video or update.message.document
    if video is None:
        return

    await update.message.reply_text("Got it, processing...")

    tg_file = await context.bot.get_file(video.file_id)
    with tempfile.NamedTemporaryFile(dir=DOWNLOAD_DIR, suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name
    await tg_file.download_to_drive(video_path)

    await process_video(update, video_path, source_url=update.message.caption or "")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    if "instagram.com" not in url:
        return

    await update.message.reply_text("Downloading reel...")

    try:
        video_path = await asyncio.to_thread(download_reel, url, DOWNLOAD_DIR)
    except Exception as exc:
        logger.exception("Failed to download reel")
        await update.message.reply_text(
            f"Couldn't download that link ({exc}). Try forwarding the reel as a video instead."
        )
        return

    await process_video(update, video_path, source_url=url)


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()

    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("url"), handle_link))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
