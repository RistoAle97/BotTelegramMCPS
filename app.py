from telegram.ext import *
from telegram import Update, ForceReply, ParseMode
import pymongo
import logging
import os

_client = pymongo.MongoClient(
    "mongodb+srv://nikodallanoce:pieroangela@clustertest.zbdu9.mongodb.net/Enterprise?retryWrites=true&w=majority")
_db = _client["Enterprise"]
customers = _db["Customers"]
topic = _db["Topics"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!, setup the bot by using the /setup command and follow all the steps',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "*List of commands:*\n\n"
        "*Utils*\n"
        "/help - Shows a list of all possible commands\n"
        "/setup - Setup the bot for your needs\n",
        parse_mode=ParseMode.MARKDOWN
    )


def setup_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Inserisci il nome col quale verrai registrato nel sistema")
    context.bot.send_message(-549095250, "Prova invio chat")


def users_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    # update.message.reply_text("Inserisci il nome col quale verrai registrato nel sistema")
    users = customers.find()
    # update.message.reply_text()
    out = ""
    for user in users:
        out += "Nome cliente: {0}, contatto Telegram: {1}\n".format(user["name"], user["chat_id"])

    update.message.reply_text("*Lista dei clienti del nostro servizio:*\n" + out, parse_mode=ParseMode.MARKDOWN)

    # context.bot.send_message(-549095250, "Prova invio chat")


def main():
    token = "1794376012:AAFqfMrJD-axHouu8feNxbaixDgP9i4M7LI"
    port = int(os.environ.get("PORT", "8443"))
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setup", setup_command))
    dispatcher.add_handler(CommandHandler("users", users_command))

    # dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # heroku_name = os.environ.get("HEROKU_APP_NAME")
    # updater.start_webhook(listen="0.0.0.0", port=port, url_path=token)
    # updater.bot.set_webhook("https://{0}.herokuapp.com/{1}".format(heroku_name, token))
    updater.idle()


if __name__ == '__main__':
    main()
