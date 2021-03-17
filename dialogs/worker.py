from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .util import state
import logging
from google_docs import GoogleDoc

logger = logging.getLogger('bot')


@state()
def start(bot, update, user_data):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Начать', callback_data='GET_START')],
    ])
    update.effective_user.send_message("Главное меню", reply_markup=reply_markup)
    return car


@state(on='button')
def car(bot, update, user_data):
    data = update.callback_query.data
    if data == 'GET_START':
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('Список машин', callback_data='LIST')],
            [InlineKeyboardButton('Ввести часть номера', callback_data='PART')],
        ])
        update.effective_user.send_message("Выберите машину", reply_markup=reply_markup)
        return choose_car
    else:
        return start(bot, update, user_data)



@state(on='button')
def choose_car(bot, update, user_data):
    data = update.callback_query.data
    if data == 'LIST':
        return car_button(bot, update, user_data)
    elif data == 'PART':
        update.effective_user.send_message("Введите часть или полный номер машины:")
        return get_car_message


@state(on='message')
def get_car_message(bot, update, user_data):
    data = update.message.text
    return car_button(bot, update, user_data, condition=data)


def car_button(bot, update, user_data, condition=False):
    gd = GoogleDoc()
    cars = gd.get_list_values('лист машин')
    if condition:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(car, callback_data=f'{car}')]
                for car in cars[cars.columns[3]] if condition in car
        ])
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(car, callback_data=f'{car}')]
            for car in cars[cars.columns[3]]
        ])

    if reply_markup.inline_keyboard:
        update.effective_user.send_message("Выберите номер машины:", reply_markup=reply_markup)
        return service
    else:
        update.effective_user.send_message("Не нашел я таких номеров:")
        return start(bot, update, user_data)


@state(on='button')
def service(bot, update, user_data):
    data = update.callback_query.data
    user_data['car'] = data

    gd = GoogleDoc()
    services = gd.get_list_values('услуги')
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(service, callback_data=f'{num}')]
        for num, service in enumerate(services[services.columns[0]])
    ])
    update.effective_user.send_message("Выбор услуги:", reply_markup=reply_markup)
    return choose_price


@state(on='button')
def choose_price(bot, update, user_data):
    data = update.callback_query.data
    gd = GoogleDoc()
    services = gd.get_list_values('услуги')
    user_data['service'] = services[services.columns[0]][int(data)]
    price = services[services.columns[2]][int(data)]
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'{price}', callback_data=f'{price}')],
        [InlineKeyboardButton('Напечатаю сам', callback_data=f'PART')]
    ])
    update.effective_user.send_message("Укажи цену:", reply_markup=reply_markup)
    return way_price


@state(on='button')
def way_price(bot, update, user_data):
    data = update.callback_query.data
    if data.isdigit():
        data = update.callback_query.data
        user_data['price'] = data
        update.effective_user.send_message("Напиши пробег:")
        return walked
    elif data == 'PART':
        update.effective_user.send_message("Введи цену:")
        return get_price_message


@state(on='message')
def get_price_message(bot, update, user_data):
    data = update.message.text
    if data.isdigit():
        user_data['price'] = data
        update.effective_user.send_message("Напиши пробег:")
        return walked
    else:
        update.effective_user.send_message("Ты чё пёс, цену не можешь нормально ввести?\nВВОДИ ЗАНОВО!")
        return get_price_message


@state(on='message')
def walked(bot, update, user_data):
    data = update.message.text
    if data.isdigit():
        user_data['walk'] = data
        message = f'''
Машина:    |  {user_data['car']}
Вид работ: |  {user_data['service']}
Цена:            |  {user_data['price']}
Пробег:       |  {user_data['walk']}
'''
        update.effective_user.send_message(message)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('ДА', callback_data='YES')],
            [InlineKeyboardButton('❗НЕТ❗', callback_data='NO')],
        ])
        update.effective_user.send_message("Сохраняем?", reply_markup=reply_markup)
        return save_info
    else:
        update.effective_user.send_message("Обычно пробег это число!")
        return walked


@state(on='button')
def save_info(bot, update, user_data):
    data = update.callback_query.data
    if data == 'YES':
        if update.effective_user.first_name or update.effective_user.last_name:
            name = update.effective_user.first_name + ' ' + update.effective_user.last_name
        else:
            name = update.effective_user.username
        gd = GoogleDoc()
        gd.spend_service(
            user_data.pop('car'),
            user_data.pop('service'),
            user_data.pop('price'),
            user_data.pop('walk'),
            name
        )
        update.effective_user.send_message(
            "Изменение внесено!")
        update.effective_user.send_message("Допустим сохранил".upper())
    else:
        update.effective_user.send_message("Ну и пиши сначала")

    return start(bot, update, user_data)
