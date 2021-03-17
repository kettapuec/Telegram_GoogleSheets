import logging
from telegram.ext import Updater
from settings import TOKEN, WORKERS
import os
from dialogs import main_handler
from datetime import datetime, time, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
import time

# Enable logging
logger = logging.getLogger('bot')
logger.propagate = False
logger.setLevel(logging.INFO)
fileHandler = logging.FileHandler(os.path.join(os.getcwd(), "bot.log"), encoding='utf-8')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
logger.addHandler(fileHandler)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def start_bot():
    # Create the Updater and pass it your bot's token.

    updater = Updater(TOKEN)
    # updater = Updater(TOKEN, use_context=True)
    # updater = Updater(TOKEN)	
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(main_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(poll_interval=2, timeout=30)





