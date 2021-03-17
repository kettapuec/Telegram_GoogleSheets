from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, run_async
from telegram.utils.promise import Promise
from collections import defaultdict
from inspect import signature
import types
import logging
from time import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger('bot')


STATE_END = ConversationHandler.END
LONG_ANSWER_THRESHOLD = 2  # seconds

states = {}


def get_func_id(func):
    return '{}.{}'.format(func.__module__, func.__name__)


def unpack(raw_result):
    if raw_result is STATE_END:
        return raw_result
    elif isinstance(raw_result, str):
        return raw_result
    elif isinstance(raw_result, types.FunctionType):
        if raw_result.dialog_id not in states:
            logger.error('Unknown state:', raw_result.dialog_id)
        return raw_result.dialog_id
    else:
        raise ValueError()


def state(on=None, max_len=None):
    def decorator(func):
        @run_async
        def wrapped(bot, update, *args, **kwargs):
            start_time = time()
            user_name = update.effective_user.full_name or update.effective_user.id

            if on == 'message':
                logger.info(f'{user_name} - message - {update.message.text}')
            if on in ('button', 'button_save'):
                logger.info(f'{user_name} - button - {update.callback_query.data}')

            logger.info(f'{user_name} - enter - {get_func_id(func)}')

            if on == 'button':
                # при переходе в новое состояние после нажатия кнопки - удаляем старые кнопки
                update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[]]))

            if on == 'message' and max_len is not None and len(update.message.text) > max_len:
                # проверяем введённое значение на ограничение по длине
                logger.info(f'{user_name} - message max len exceeded - {len(update.message.text)}>{max_len}')
                update.effective_user.send_message('❗ Значение должно быть не длиннее {} символов!\n'
                                                   'Пожалуйста, введите заново:'.format(max_len))
                return wrapped.dialog_id
            elif on == 'message' and len(update.message.text) < 1:
                logger.info(f'{user_name} - message was empty ')

            try:
                res = func(bot, update, *args, **kwargs)
            except Exception as e:
                logger.exception(f'ERROR: {user_name} - {get_func_id(func)}')
                update.effective_user.send_message('Что-то пошло не так!😕\nНачните сначала /start')
                res = STATE_END

            dt = time() - start_time
            if dt >= LONG_ANSWER_THRESHOLD:
                logger.warning(f'LONG ANSWER: {dt:.1f}s for {user_name} - {get_func_id(func)}')

            if isinstance(res, Promise):
                return unpack(res.result())
            else:
                return unpack(res)

        func_id = get_func_id(func)
        wrapped.dialog_id = func_id
        pass_user_data = 'user_data' in signature(func).parameters
        if on == 'button':
            states[func_id] = [CallbackQueryHandler(wrapped, pass_user_data=pass_user_data)]
        elif on == 'button_save':  # с эти параметром старые кнопки не удаляем
            states[func_id] = [CallbackQueryHandler(wrapped, pass_user_data=pass_user_data)]
        elif on == 'message':
            states[func_id] = [MessageHandler(Filters.text, wrapped, pass_user_data=pass_user_data)]
        return wrapped
    return decorator
