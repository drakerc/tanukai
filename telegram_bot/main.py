import logging
from io import BytesIO

import requests
from telegram import __version__ as TG_VER, MessageEntity, File

try:
    from telegram import __version_info__
except ImportError as e:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TANUKAI_API_URL = "https://tanukai.com/api/v1"
from . import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


def _prepare_results_message(response_json: dict) -> str:
    similar_images = response_json["similar_images"]

    reply_message = "Most similar results:\n"
    for i in range(config.SIMILAR_IMAGES_RETURNED):
        similar_image = similar_images[i]
        source_url = similar_image["data"]["source_image_url"]
        similarity = similar_image["distance"]
        is_nsfw = similar_image["data"]["source_rating"] != "safe"
        reply_message += f"- {source_url} - {similarity}% similar"
        reply_message += " - NSFW\n" if is_nsfw else "\n"

    return reply_message


async def upload_image_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await context.bot.get_file(update.message.photo[-1].file_id)

    api_url = f"{TANUKAI_API_URL}/upload-by-url"

    response = requests.post(
        api_url,
        json={
            "image_url": file.file_path,
            "maximum_rating": "explicit",
            "partitions": ["e621", "furaffinity"]
        },
        timeout=15,
        stream=True,
        headers={"User-Agent": "Tanukai.com Telegram Bot"},
    )
    response_json = response.json()

    reply_message = _prepare_results_message(response_json)

    await update.message.reply_text(reply_message)


async def url_image_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_url = f"{TANUKAI_API_URL}/upload-by-url"

    response = requests.post(
        api_url,
        json={
            "image_url": update.message.text,
            "maximum_rating": "explicit",
            "partitions": ["e621", "furaffinity"]
        },
        timeout=15,
        stream=True,
        headers={"User-Agent": "Tanukai.com Telegram Bot"},
    )
    response_json = response.json()

    reply_message = _prepare_results_message(response_json)

    await update.message.reply_text(reply_message)


def main() -> None:
    bot_token = config.BOT_TOKEN
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & (filters.Entity(MessageEntity.URL) | filters.Entity(MessageEntity.TEXT_LINK)), url_image_search))

    # application.add_handler(MessageHandler(filters.Document.Category("image/"), upload_image_search))
    application.add_handler(MessageHandler(filters.Document.IMAGE, upload_image_search))
    application.add_handler(MessageHandler(filters.PHOTO, upload_image_search))


    application.run_polling()


if __name__ == "__main__":
    main()
