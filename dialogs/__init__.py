import dialogs.auth as auth
import dialogs.worker as worker

from .util import states

from telegram.ext import (CommandHandler, ConversationHandler)


# общий колбэк для прерывания диалога
def stop(bot, update):
    return ConversationHandler.END


# общий фолбэк и точка входа
fallback = [
    CommandHandler('stop', stop, pass_user_data=True),
    CommandHandler('start', auth.start, pass_user_data=True),
]
entry_points = [
    CommandHandler('start', auth.start, pass_user_data=True),
]

main_handler = ConversationHandler(entry_points=entry_points, states=states, fallbacks=fallback)
