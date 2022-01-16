from telegram.ext.updater import Updater
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext.filters import Filters
import telegram

from conn_db import query_meme
import requests
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def semantic_api(text):
    answer = requests.get('http://localhost:8000/', params={'query': str(text)}).json()

    return answer


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"Hey! I'm CryptoBot! How are you? You can ask me anything about cryptocurrency!")
    update.message.reply_text("Hit /help to know what I can do")
    update.message.reply_text("Or /about to know more about me")


def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""

    keyboard = [[InlineKeyboardButton(text='What is blockchain?', callback_data='1')],
                [InlineKeyboardButton(text='Is ethereum a good investment in 2022?', callback_data='2')],
                [InlineKeyboardButton(text='Give me a meme', callback_data='Give me a meme')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Try to ask me something like this:", reply_markup=reply_markup)


def query_handler(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    if query.data == '1':
        answer = semantic_api('What is blockchain?')
        query.answer(answer[0])
        query.answer(answer[1])
        query.answer(answer[2])

    elif query.data == '2':
        answer = semantic_api('Is ethereum a good investment in 2022?')
        query.answer(answer[0])
        query.answer(answer[1])
        query.answer(answer[2])
    else:
        meme = query_meme()

        query.edit_message_text(meme)
        query.edit_message_text("Funny right?")


def about_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("I use semantic search with transformers architecture to answer your questions.")
    update.message.reply_text(
        "I'm a bit slow answering your questions because I'm running on CPU. Pet project == Free tier budget!")
    update.message.reply_text("See the github repo: https://github.com/joaomsimoes/telegram-semantic_search")


def open_question(update: Update, context: CallbackContext) -> None:
    """Semantic search"""
    answer = semantic_api(update.message.text)
    try:
        if answer[0]:
            update.message.reply_text(answer[0])
            update.message.reply_text(answer[1])
    except:
        update.message.reply_text("Sorry I did not understand what you want to say")


def give_meme(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""

    meme = query_meme()

    update.message.reply_photo(meme)
    update.message.reply_text("Funny right?")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("#",
                      use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    dispatcher.add_handler(CallbackQueryHandler(query_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Meme|meme|Give meme|give meme|give me a meme|Give me a meme$'), give_meme))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, open_question))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
