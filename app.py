from telegram.ext import *
from telegram import Update, ForceReply, ParseMode
import pymongo
import logging
import os

_client = pymongo.MongoClient(
    "mongodb+srv://nikodallanoce:pieroangela@clustertest.zbdu9.mongodb.net/Mqttemp?retryWrites=true&w=majority")
_db = _client["Mqttemp"]
customers = _db["Customers"]
topics = _db["Topics"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!, use the /help command if you need to look at all the possible commands',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "*List of commands:*\n\n"
        "*/help*\n"
        "Shows a list of all possible commands\n\n"
        # "/setup - Setup the bot for your needs\n",
        "*/topics [topic]*\n"
        "Shows every topic you're subscribed to (if no argument is passed), "
        "by using an argument you can look for specific topics, example: /topics userName/subtopic will return all the"
        " topics that fall in userName/subtopic\n",
        parse_mode=ParseMode.MARKDOWN
    )


def users_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    users = customers.find()
    out = ""
    for user in users:
        out += "Nome cliente: {0}, contatto Telegram: {1}\n".format(user["name"], user["chat_id"])

    update.message.reply_text("*Lista dei clienti del nostro servizio:*\n" + out, parse_mode=ParseMode.MARKDOWN)


def topics_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /topics is issued."""
    chat_id = update.message.chat.id
    if len(context.args) > 1:
        update.message.reply_text("Hai inserito troppi argomenti al comando /topics")
        return

    user = customers.find_one({"chatID": chat_id})
    if context.args:
        user_topics = topics.find(
            {"name": {'$regex': context.args[0]+'/'},
             "customerID": user["_id"]}
        )
    else:
        user_topics = topics.find({"customerID": user["_id"]})

    if not user:
        update.message.reply_text("Non sei registrato nel sistema")
    elif topics.count_documents({"customerID": user["_id"]}) == 0:
        update.message.reply_text("Non esiste alcun topic associato col tuo nome/chat: {0}".format(user["name"]))
    else:
        out = "*List of the topics you're subscribed to as {0}:*\n".format(user["name"])
        for topic in user_topics:
            out += "Topic: {0}, Offset: {1}\n".format(topic["name"], topic["samplingInterval"])

        update.message.reply_text(out, parse_mode=ParseMode.MARKDOWN)


def main():
    token = "1794376012:AAFqfMrJD-axHouu8feNxbaixDgP9i4M7LI"
    port = int(os.environ.get("PORT", "8443"))
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("users", users_command))
    dispatcher.add_handler(CommandHandler("topics", topics_command))

    # dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # heroku_name = os.environ.get("HEROKU_APP_NAME")
    # updater.start_webhook(listen="0.0.0.0", port=port, url_path=token)
    # updater.bot.set_webhook("https://{0}.herokuapp.com/{1}".format(heroku_name, token))
    updater.idle()


if __name__ == '__main__':
    main()
