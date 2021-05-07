from telegram.ext import *
from telegram import Update, ForceReply, ParseMode, BotCommand
import pymongo
import numpy as np
import logging
import datetime
import os

mongoclient = os.environ.get("mongoclient")
_client = pymongo.MongoClient(mongoclient)
_db = _client["Mqttempv2"]
customers = _db["Customers"]
topics = _db["Topics"]
records = _db["Records"]
alerts = _db["Alerts"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!, use the /help command if you need to look at all the possible commands',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "*Utils:*\n"
        "/help - "
        "Shows a list of all possible commands\n"
        "/user - "
        "Shows informations about you\n"
        "/topics *topic* - "
        "Shows every topic you're subscribed to (if no argument is passed)\n"
        "\n*Modify Parameters*\n"
        "/changeoffset *topic offset* - "
        "Changes the smapling interval of the desired topic (you're subscribed to)\n"
        "/changetrigger *topic trigger* - "
        "Changes the trigger condition of the desired topic (you're subscribed to)\n"
        "/setalert *topic offset* - "
        "Changes the alert offset of the desired topic (you're subscribed to)\n"
        "\n*Return Records*\n"
        "/avgtemp *topic year-month-day* - "
        "Gives the average temperature of the current day if no argument is passed\n"
        "/avghum *topic year-month-day* - "
        "Gives the average humidity of the current day if no argument is passed\n"
        "/lasttemp *topic year-month-day* - "
        "Returns the last recorded temperature of the current day if no argument is passed\n"
        "/lasthum *topic year-month-day* - "
        "Returns the last recorded humidity of the current day if no argument is passed\n",
        parse_mode=ParseMode.MARKDOWN
    )


def topics_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /topics is issued."""
    chat_id = update.message.chat.id
    if len(context.args) > 1:
        update.message.reply_text("You have inserted too many arguments to the commmand /topics")
        return

    user = customers.find_one({"chatID": chat_id})
    if not user:
        update.message.reply_text("You're not registered in our system")
        return

    if context.args:
        user_topics = topics.find(
            {"name": {'$regex': context.args[0] + '/'},
             "customerID": user["_id"]}
        )
    else:
        user_topics = topics.find({"customerID": user["_id"]})

    if topics.count_documents({"customerID": user["_id"]}) == 0:
        update.message.reply_text("There's no topic linked to your name /chat: {0}".format(user["name"]))
    else:
        out = "*List of the topics you're subscribed to as {0}:*\n".format(user["name"])
        for topic in user_topics:
            out += "Topic: {0}, Offset: {1}, Threshold: {2}\n".format(topic["name"],
                                                                      topic["samplingInterval"], topic["triggerCond"])

        update.message.reply_text(out, parse_mode=ParseMode.MARKDOWN)


def change_offset_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /changeoffset is issued."""
    chat_id = update.message.chat.id
    if len(context.args) != 2:
        update.message.reply_text("There should be exactly two arguments to the command /changeoffset")
        return

    user = customers.find_one({"chatID": chat_id})
    if not user:
        update.message.reply_text("You're not registered in our system")
        return

    topic = context.args[0]
    offset = int(context.args[1])
    if topics.count_documents({"name": topic, "customerID": user["_id"]}) == 0:
        update.message.reply_text(
            "The topic {0} wasn't found, use /topics to look at the topics you're subscribed to".format(topic))
    else:
        topics.update_one(
            {"name": topic, "customerID": user["_id"]},
            {"$set": {"samplingInterval": offset}}
        )
        update.message.reply_text(
            "The topic {0} offset was updated successfully".format(topic))


def change_trigger_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /changetrigger is issued."""
    chat = update.message.chat.id
    if len(context.args) != 2:
        update.message.reply_text("There should be exactly two arguments to the /changetrigger command")
        return

    user = customers.find_one({"chatID": chat})
    if not user:
        update.message.reply_text("You're not registered in our system")
        return

    topic = context.args[0]
    trigger = int(context.args[1])
    if topics.count_documents({"name": topic, "customerID": user["_id"]}) == 0:
        update.message.reply_text(
            "The topic {0} wasn't found, use /topics to look at the topics you're subscribed to".format(topic))
    else:
        topics.update_one(
            {"name": topic, "customerID": user["_id"]},
            {"$set": {"triggerCond": trigger}}
        )
        update.message.reply_text(
            "The topic {0} trigger condition was updated successfully".format(topic))


def __commands_setup(update: Update, context: CallbackContext, command_type: str):
    chat = update.message.chat.id
    if len(context.args) > 2 or len(context.args) < 1:
        update.message.reply_text("Wrong arguments for the {0} command, use /help for more details".
                                  format(command_type))
        return None, None

    user = customers.find_one({"chatID": chat})
    if not user:
        update.message.reply_text("You're not registered in our system")
        return None, None

    topic = context.args[0]
    user_topic = topics.find_one({"name": topic, "customerID": user["_id"]})
    if not user_topic:
        update.message.reply_text(
            "The topic {0} wasn't found, use /topics to look at the topics you're subscribed to".format(topic))
        return None, None

    if len(context.args) == 1:
        date = datetime.datetime.today().date()
        out = "today"
    else:
        date = datetime.datetime.strptime(context.args[1], '%Y-%m-%d').date()
        out = context.args[1]

    date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    topic_records = records.find_one({
        "topicID": user_topic["_id"],
        "date": date
    })
    return topic_records, out


def average_temperature_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /avgtemp is issued."""
    temperature_records, out = __commands_setup(update, context, "/avgtemp")
    if not out:
        return

    if not temperature_records:
        update.message.reply_text("There are no records for {0} temperature".format(out))
        return

    t_list = temperature_records["temp"]
    avg_t = float(sum(temperature['val'] for temperature in t_list)) / len(t_list)
    update.message.reply_text("*Average temperature for {0}:*\n {1}".format(out, np.round(avg_t, 2)),
                              parse_mode=ParseMode.MARKDOWN)


def average_humidity_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /avghum is issued."""
    humidity_records, out = __commands_setup(update, context, "/avghum")
    if not out:
        return

    if not humidity_records:
        update.message.reply_text("There are no records for {0} humidity".format(out))
        return

    h_list = humidity_records["hum"]
    avg_h = float(sum(humidity['val'] for humidity in h_list)) / len(h_list)
    update.message.reply_text("*Average humidity for {0}:*\n {1}".format(out, np.round(avg_h)),
                              parse_mode=ParseMode.MARKDOWN)


def error(update, context: CallbackContext) -> None:
    logger.warning("Update {0} caused error {1}".format(update, context.error))


def user_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /user is issued."""
    chat = update.message.chat.id
    user = customers.find_one({"chatID": chat})
    if not user:
        update.message.reply_text("You're not registered in our system, your chat id is {0}".format(chat))
    else:
        update.message.reply_text("You're registered as user {0}, your chat id is {1}".format(user["name"], chat))


def __last_relevation_setup(relevations_records, command_type: str):
    records_list = relevations_records[command_type]
    last_record = records_list[-1]
    timestamp = last_record["time"]
    date = datetime.datetime.fromtimestamp(timestamp.inc)
    return last_record["val"], date


def last_temperature_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /lasttemp is issued."""
    temperature_records, out = __commands_setup(update, context, "/lasttemp")
    if not out:
        return

    if not temperature_records:
        update.message.reply_text("There are no records for {0} temperature".format(out))
        return

    last_temp, date = __last_relevation_setup(temperature_records, "temp")
    update.message.reply_text("*Last recorded temperature for {0}:*\n{1}, recorded at {2}"
                              .format(out, last_temp, date), parse_mode=ParseMode.MARKDOWN)


def last_humidity_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /lasthum is issued."""
    humidity_records, out = __commands_setup(update, context, "/lasthum")
    if not out:
        return

    if not humidity_records:
        update.message.reply_text("There are no records for {0} humidity".format(out))
        return

    last_hum, date = __last_relevation_setup(humidity_records, "hum")
    update.message.reply_text("*Last recorded humidity for {0}:*\n{1}, recorded at {2}"
                              .format(out, last_hum, date), parse_mode=ParseMode.MARKDOWN)


def change_alert_offset(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /setalert is issued."""
    chat_id = update.message.chat.id
    if len(context.args) != 2:
        update.message.reply_text("There should be exactly two arguments to the command /setalert")
        return

    user = customers.find_one({"chatID": chat_id})
    if not user:
        update.message.reply_text("You're not registered in our system")
        return

    topic = context.args[0]
    offset = int(context.args[1])
    if topics.count_documents({"name": topic, "customerID": user["_id"]}) == 0:
        update.message.reply_text(
            "The topic {0} wasn't found, use /topics to look at the topics you're subscribed to".format(topic))
    else:
        user_topic = topics.find_one({"name": topic, "customerID": user["_id"]})
        alerts.update_one(
            {"topicID": user_topic["_id"]},
            {"$set": {"alertOffset": offset}}
        )
        update.message.reply_text(
            "The topic {0} alert offset was updated successfully".format(topic))


def main():
    token = os.environ.get("token")
    port = int(os.environ.get("PORT", "8443"))
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("topics", topics_command))
    dispatcher.add_handler(CommandHandler("changeoffset", change_offset_command))
    dispatcher.add_handler(CommandHandler("changetrigger", change_trigger_command))
    dispatcher.add_handler(CommandHandler("avgtemp", average_temperature_command))
    dispatcher.add_handler(CommandHandler("avghum", average_humidity_command))
    dispatcher.add_handler(CommandHandler("user", user_command))
    dispatcher.add_handler(CommandHandler("lasttemp", last_temperature_command))
    dispatcher.add_handler(CommandHandler("lasthum", last_humidity_command))
    dispatcher.add_handler(CommandHandler("setalert", change_alert_offset))

    commands = [
        BotCommand("start", "Starts the bot"),
        BotCommand("help", "Shows a list of all possible commands"),
        BotCommand("user", "Shows informations about you"),
        BotCommand("topics", "Shows every topic"),
        BotCommand("changeoffset", "Changes the sampling interval"),
        BotCommand("changetrigger", "Changes the threshold"),
        BotCommand("setalert", "Changes the alert offset"),
        BotCommand("avgtemp", "Returns the temperature of a topic"),
        BotCommand("avghum", "Returns the humidity of a topic"),
        BotCommand("lasttemp", "Returns the last recorded temperature of a topic"),
        BotCommand("lasthum", "Returns the last recorded humidity of a topic")]
    dispatcher.bot.set_my_commands(commands)

    dispatcher.add_error_handler(error)

    # Start the Bot
    # updater.start_polling()
    heroku_name = os.environ.get("bot_name")
    updater.start_webhook(listen="0.0.0.0", port=port, url_path=token,
                          webhook_url="https://{0}.herokuapp.com/{1}".format(heroku_name, token))
    updater.idle()


if __name__ == '__main__':
    main()
