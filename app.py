from telegram.ext import *
from telegram import Update, ForceReply, ParseMode
# import pymongo
import logging
# import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # bot = context.bot
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("List of ccommands:\n\n"
                              "*Utils*\n"
                              "/help - Shows a list of all possible commands\n"
                              "/setup - Setup the bot for your needs",
                              parse_mode=ParseMode.MARKDOWN)
    # update.message.reply_text('Help!')


def setup_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Inserisci il nome col quale verrai registrato nel sistema")


def main():
    token = "1794376012:AAFqfMrJD-axHouu8feNxbaixDgP9i4M7LI"
    # port = int(os.environ.get("PORT", "8443"))
    port = 1990
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setup", setup_command))

    # dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # heroku_name = os.environ.get("HEROKU_APP_NAME")
    # updater.start_webhook(listen="0.0.0.0", port=port, url_path=token)
    # updater.bot.set_webhook("https://{0}.herokuapp.com/{1}".format(heroku_name, token))
    updater.idle()

    # updater.idle()


if __name__ == '__main__':
    main()
