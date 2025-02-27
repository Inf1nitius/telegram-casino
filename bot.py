import logging
from dotenv import load_dotenv
from os import getenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=update.effective_chat.id, text="bot working")


async def echo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )

async def quiz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if '/∞' in update.message.text:
        await ctx.bot.send_message(
            chat_id='443746339', text=update.message.text
    )


if __name__ == "__main__":
    load_dotenv()
    TOKEN = getenv("TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), quiz)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()