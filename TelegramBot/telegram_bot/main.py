from telegram.ext.updater import Updater
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext.filters import Filters
import telegram

from utils import *
import logging
import random

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        f"Hey! I'm CryptoBot! How are you? You can ask me anything about cryptocurrency!")
    update.message.reply_text("Hit /help to know what I can do")
    update.message.reply_text("Or /about to know more about me")


def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""

    keyboard = [[InlineKeyboardButton(text='What is blockchain?', callback_data='1')],
                [InlineKeyboardButton(text='Is ethereum a good investment in 2022?', callback_data='2')],
                [InlineKeyboardButton(text='Give me a meme', callback_data='3')]]

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
        update.effective_message.reply_text(answer[0])
        update.effective_message.reply_text(answer[1])

    elif query.data == '2':
        answer = semantic_api('Is ethereum a good investment in 2022?')
        update.effective_message.reply_text(answer[0])
        update.effective_message.reply_text(answer[1])
    else:
        meme = query_meme()
        update.effective_message.reply_photo(meme)
        messages = ["Funny right?", "What you think about this meme?!", "You want another one?"]

        keyboard = [[InlineKeyboardButton(text='Another one!', callback_data='3')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.effective_message.reply_text(random.choice(messages), reply_markup=reply_markup)


def about_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("I use semantic search with transformers architecture to answer your questions. 🤖")
    update.message.reply_text(
        "I'm a bit slow answering your questions because I'm running on CPU. Pet project == Free tier budget! ✌")
    update.message.reply_text("See the github repo: https://github.com/joaomsimoes/semantic_search")


def open_question(update: Update, context: CallbackContext) -> None:
    """Semantic search"""
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING, timeout=20)
    answer = semantic_api(update.message.text)
    try:
        if answer[0]:
            update.message.reply_text(answer[0])
            update.message.reply_text(answer[1])
    except:
        update.message.reply_text("Sorry I did not understand what you want to say")


def give_meme(update: Update, context: CallbackContext):
    """Gives a meme"""

    meme = query_meme()

    update.message.reply_photo(meme)

    messages = ["Funny right?", "What you think about this meme?!", "You want another one?"]

    keyboard = [[InlineKeyboardButton(text='Another one!', callback_data='3')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(random.choice(messages), reply_markup=reply_markup)


def coin_handler(update: Update, context: CallbackContext):
    """Answer about coin"""
    answer = coin_ner(update.message.text)
    try:
        update.message.reply_text(answer)
    except:
        update.message.reply_text("Sorry I did not understand what you want to say")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    f = open("keys.json")
    data = json.load(f)
    updater = Updater(data["Telegram"],
                      use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    dispatcher.add_handler(CallbackQueryHandler(query_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Meme|meme|Give meme|give meme|give me a meme|Give me a meme$'), give_meme))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(
            '^price from .*|Price from .*|current price from .*|Current price from .*|'
            'value from .*|Value from .*$'
        ), coin_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, open_question))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


# |bitcoin|Bitcoin|BTC|Btc|btc|Ethereum|ethereum|ETH|Eth|eth|'
# 'Tether|tether|USDT|Usdt|usdt|BNB|Bnb|bnb|Cardano|cardano|ADA|Ada|ada|USD Coin|USDC|Usdc|'
# 'Solana|solana|SOL|sol|Sol|XPR|Xpr|xpr|Terra|terra|LUNA|Luna|luna|Polkadot|polkadot|DOT|dot|Dot|'
# 'Dogecoin|dogecoin|doge|DOGE|Doge|Avalanche|avalanche|AVAX|Avax|avax|Polygon|polygon|MATIC|Matic|matic|'
# 'Shiba|shiba|Shiba Inu|shiba inu|Shiba inu|shiba Inu|SHIB|Shib|shib|Litecoin|litecoin|ltc|Ltc|LTC

if __name__ == '__main__':
    main()
