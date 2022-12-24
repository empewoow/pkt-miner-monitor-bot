import constants
from telegram.ext import *
from telegram import ParseMode
import responses
import miner_info
import data
import datetime
import pytz

# https://stackoverflow.com/questions/62289341/telegram-bot-api-python-run-daily-method
# https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#message-formatting-bold-italic-code-

def start_command(update, context):
    #update.message.reply_text("Type something to get started!")

    # Send a message every hour:
    #context.job_queue.run_repeating(callback_message, interval=3600, first=1, context=update.message.chat_id)

    # Send the daily message at 9:30 Europe (Amsterdam) time:
    context.job_queue.run_daily(daily_message,
                                datetime.time(hour=9, minute=30, tzinfo=pytz.timezone('Europe/Amsterdam')),
                                days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)

def callback_message(context):
    chat_id = context.job.context
    #now = datetime.datetime.now()
    #time = now.strftime("%H:%M")
    
    addresses = data.get_addresses(chat_id)
    message = miner_info.get_miner_info(addresses)

    context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)

def daily_message(context):
    chat_id = context.job.context
    #now = datetime.datetime.now()
    #time = now.strftime("%H:%M")

    addresses = data.get_addresses(chat_id)
    message = miner_info.get_miner_info(addresses)

    context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)

def list_addresses_command(update, context):
    chat_id = update.message.chat_id
    message = update.message.text.lower()
    result = data.list_addresses(chat_id, message)
    update.message.reply_text(result)

def add_address_command(update, context):
    chat_id = update.message.chat_id
    message = update.message.text.lower()
    result = data.add_address(chat_id, message)
    update.message.reply_text(result)

def remove_address_command(update, context):
    chat_id = update.message.chat_id
    message = update.message.text.lower()
    result = data.remove_address(chat_id, message)
    update.message.reply_text(result)

def check_command(update, context: CallbackContext):
    update.message.reply_text(f"Check: {context.bot.base_url}")

def help_command(update, context):
    update.message.reply_text("If you need help? Ask Google lol.")

def handle_message(update, context):
    message = update.message.text.lower()
    response = responses.sample_responses(message)
    update.message.reply_text(response)

def error(update, context):
    print(f"Update {update} caused error {context.error}.")

def main():

    data.create_table()
    
    updater = Updater(constants.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("list_addresses", list_addresses_command))
    dp.add_handler(CommandHandler("add_address", add_address_command))
    dp.add_handler(CommandHandler("remove_address", remove_address_command))
    dp.add_handler(CommandHandler("check", check_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()

    print ("PKT Miner Monitor bot started.")

    updater.idle()

main()