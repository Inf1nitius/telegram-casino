import asyncio
from dotenv import load_dotenv
import logging
from os import getenv
import toml

from telegram import Bot, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from resources.create_cards import create_cards_txt
from singleplayer import highlow

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await ctx.bot.send_message(chat_id=update.effective_chat.id, text="bot working")


async def start_highlow(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await highlow.start(update, ctx)


async def register_commands(application: Application) -> None:
    config = toml.load("config.toml")
    commands = [
        (command["name"], command["description"]) for command in config["commands"]
    ]
    print(f"registering commands:\n{commands}")
    await application.bot.set_my_commands(commands)


if __name__ == "__main__":
    load_dotenv()
    TOKEN = getenv("TOKEN")

    create_cards_txt(toml.load("config.toml"))

    application = ApplicationBuilder().token(TOKEN).post_init(register_commands).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("highlow", start_highlow))
    application.add_handler(CallbackQueryHandler(highlow.callback_handler))

    application.run_polling()
