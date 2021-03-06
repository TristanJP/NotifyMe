#!/usr/bin/env python3

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import json
import logging
import re
import requests
import lxml
from bs4 import BeautifulSoup

import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    filename='logs/notify_me.log',
)

logger = logging.getLogger(__name__)

# The API Key we received for our bot
with open("telegram_legacy_bot.conf", "r") as config_file:
    config = json.load(config_file)

    API_KEY = config.get("API_KEY", None)
    if API_KEY is None:
        logger.info("API KEY not found!")

    eden_pages = config.get("eden_pages", None)
    if eden_pages is None:
        logger.info("No Eden webpages known.")


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def eden_in_stock(number):
    if number in eden_pages:
        eden_url = eden_pages[number]

        source = requests.get(eden_url).text
        soup = BeautifulSoup(source, 'lxml')
        stock_tag = soup.find('span', class_="instock")

        return stock_tag is not None


def get_job(message):
    job = re.match(r"^/check (.*)", message)
    return job.group(1)


def check(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    #update.message.reply_text(f"Checking job: {get_job(update.message.text)}")
    # update.message.reply_text("Hello there, do you want to answer a question? (Yes/No)",
    #     reply_markup=telegram.ReplyKeyboardMarkup([['101', '172']], one_time_keyboard=True)
    # )
    number = get_job(update.message.text)
    in_stock = eden_in_stock(number)

    in_stock_text = f"Eden {number} "
    if in_stock is None:
        in_stock_text += "is not known."
    elif in_stock:
        in_stock_text += "is in Stock!"
    else:
        in_stock_text += "is NOT in Stock."

    logger.info(f"{in_stock}: {in_stock_text}")
    update.message.reply_text(in_stock_text)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("check", check))

    # on noncommand i.e message - echo the message on Telegram
    #dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
