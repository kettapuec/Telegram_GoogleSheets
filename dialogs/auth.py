from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from .util import state
from settings import WORKERS
import dialogs
logger = logging.getLogger('bot')


@state()
def start(bot, update, user_data):
    # Если пользователя нет в конфиге выдаем телеграмм id вошедшего пользователя
    user_id = update.effective_user.id
    user_data['user'] = user_id
    for worker in WORKERS:
        if user_id == worker['id']:
            return dialogs.worker.start(bot, update, user_data)

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Я передал свой id администратору', callback_data='RE_LOGIN')]
    ])
    update.effective_user.send_message(text='Ваш телеграмм ID:')
    update.effective_user.send_message(text=f'{user_id}', reply_markup=reply_markup)
    return auth


@state(on='button')
def auth(bot, update):
    data = update.callback_query.data
    if data == 'RE_LOGIN':
        return start(bot, update)
    else:
        logger.warning('Попали в исключение')
        return start(bot, update)

