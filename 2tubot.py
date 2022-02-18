
"""
In order to support the CRM processes in our company and to optimize the handling of customers 
in our  front offices, the R&D department explores the possibility of working with an automated 
chatbot through the Telegram platform.

"""

import logging
from typing import Dict
import os
from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# the list of code in our company system.
list_code= ['A111',"A112","A113","A114",'A115',"A116","A117","A118"]


logger = logging.getLogger(__name__)

# States
CHOOSING, TYPING_REPLY, TYPING_CHOICE, CHOOSING2= range(4)

reply_keyboard = [
    ['Track my code', 'Other'],
    ['End'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


reply_keyboard2 = [
    ['Main menu', 'Search'],
    ['End'],
]
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)

#start_function
def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
   
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(f"👋 Hi {user.first_name}, are you intrested in our sevices, choose what you want in the menu bellow 👇:", reply_markup=markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return CHOOSING

def start_over(update: Update, context: CallbackContext) -> int:
    """Just to handel the case when the customers type sommeting"""
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Sorry! Did you mean ? (Choose from buttons bellow 👇)", reply_markup=markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return CHOOSING


def track_mycode(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the code to track."""
    update.message.reply_text(f'Please type your code:')

    return TYPING_REPLY

def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text

    if text in list_code:
        update.message.reply_text(
            f"✅ Yes, your code '{text}' is on the system",
            reply_markup=markup2,
        )
    else:
        update.message.reply_text(
            f"❌ No, your code '{text}' isn't on the system",
            reply_markup=markup2,
        )

    return CHOOSING2

def other(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data

    update.message.reply_text(
        "Sorry, this is the services that we offre right now 👇:",
        reply_markup=markup
    )

    return CHOOSING

def end(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data

    update.message.reply_text(
        f"Bye! (if you want to talk to me just type '/start')"
    )

    return ConversationHandler.END

def main() -> None:
    """Run the bot."""

    # setting to appropriate values
    TOKEN = os.getenv("TOKEN")
    APPNAME = os.getenv("APPNAME")
    # set PORT to be used with Heroku
    PORT = os.environ.get('PORT')

    # the Updater is the essentiel element to run the bot.
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Track my code|Search)$'), track_mycode
                ),
                MessageHandler(
                    Filters.regex('^(Hi|hi|Hello|hello)$'), start
                ),
                MessageHandler(
                    Filters.regex('^Other$'), other
                ),
                MessageHandler(
                    Filters.text, start_over
                )
            ],
            
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^End$')),
                    received_information,
                )
            ],
            CHOOSING2: [
                MessageHandler(
                    Filters.regex('^Main menu$'),
                    start,
                ),
                MessageHandler(
                    Filters.regex('^Search$'),
                    track_mycode,
                )
            ],

            TYPING_CHOICE: [
                MessageHandler(
                    Filters.regex('^Search$'),
                    track_mycode,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^End$'), end)],
    )

    dispatcher.add_handler(conv_handler)

    # starting webhook and setting it up with heroku app
    updater.start_webhook(listen="0.0.0.0",
                            port=(PORT),
                            url_path=TOKEN)
    
    updater.bot.setWebhook(
      "https://{}.herokuapp.com/{}".format(APPNAME, TOKEN)
    )
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
