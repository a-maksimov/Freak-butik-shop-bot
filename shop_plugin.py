import json
import os

import config
from start import handle_start_help
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_calendar import WYearTelegramCalendar
from datetime import date

import text
from correct_number import correct_number
from SQLighter import SQLighter

LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

# Создание таблиц БД, если их нет
SQLighter(config.database_name).create_clients()
SQLighter(config.database_name).create_shop()
SQLighter(config.database_name).create_piercing()
SQLighter(config.database_name).close()


# Функции управления БД
# Функция добавления нового клиента
def add_client(client):
    db_worker = SQLighter(config.database_name)
    db_worker.add_client(client)
    db_worker.close()


# Функция добавления доп. данных клиента
def update_client(user_id, first_name, last_name, phone):
    db_worker = SQLighter(config.database_name)
    db_worker.update_client(user_id, first_name, last_name, phone)
    db_worker.close()


# Функция получения продукта из БД
def get_product(product_id):
    db_worker = SQLighter(config.database_name)
    product = db_worker.get_product(product_id)
    db_worker.close()
    return product


# Функция просмотра уровня доступа
def get_access(user_id):
    db_worker = SQLighter(config.database_name)
    access = db_worker.get_access(user_id)
    db_worker.close()
    return access


# Функция просмотра профиля клиента
def view_client(user_id):
    db_worker = SQLighter(config.database_name)
    profile = db_worker.view_client(user_id)
    db_worker.close()
    return profile


# Функция добавления даты записи
# TODO: user_id is not unique for client if someone gets booked by another user_id
# TODO: and phone can't be passed to booking; try using increment id for booking
def add_booking(call, user_id, result):
    date_booked = (result.year, result.month, result.day)
    cal_id = int(call.data.split('_')[1])
    if cal_id == 1:
        table = 'calendar_piercing'
    db_worker = SQLighter(config.database_name)
    db_worker.add_booking(user_id, table, date_booked)
    db_worker.close()


# Функции разметки кнопок
# Лэндинг на магазин
def markup_shop():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Профиль 🥷', callback_data='profile')
    item2 = InlineKeyboardButton('Коллекции', callback_data='collections')
    markup.row(item1, item2)
    item3 = InlineKeyboardButton('Женское', callback_data='women')
    item4 = InlineKeyboardButton('Мужское', callback_data='men')
    markup.row(item3, item4)
    item4 = InlineKeyboardButton('Назад', callback_data='start')
    item5 = InlineKeyboardButton('Скрыть', callback_data='hide')
    markup.row(item4, item5)
    return markup


def markup_back_to_landing():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Назад в магазин', callback_data='start')
    item2 = InlineKeyboardButton('Скрыть', callback_data='hide')
    markup.row(item1, item2)
    return markup


# Страница продукта
def markup_product(count, page, url):
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton(text='⬅', callback_data="{\"method\":\"pagination\","
                                                         "\"NumberPage\":" + str(page - 1) + ","
                                                                                             "\"CountPage\":" + str(
        count) + "}")
    item2 = InlineKeyboardButton(text=f'{page}/{count}', callback_data=' ')
    item3 = InlineKeyboardButton(text='➡', callback_data="{\"method\":\"pagination\","
                                                         "\"NumberPage\":" + str(page + 1) + ","
                                                                                             "\"CountPage\":" + str(
        count) + "}")
    if page == 1:
        markup.row(item2, item3)
    elif page == count:
        markup.row(item1, item2)
    else:
        markup.row(item1, item2, item3)
    item4 = InlineKeyboardButton(text='Купить на сайте', url=url)
    item5 = InlineKeyboardButton(text='Купить с QIWI', callback_data='buy')
    markup.row(item4, item5)
    item6 = InlineKeyboardButton(text='Назад', callback_data='shop')
    item7 = InlineKeyboardButton(text='Скрыть', callback_data='hide')
    markup.row(item6, item7)
    return markup


# Просмотр профиля
def markup_profile():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Назад', callback_data='shop')
    item2 = InlineKeyboardButton('Список покупок', callback_data='bought')
    markup.row(item1, item2)
    item3 = InlineKeyboardButton('Сменить телефон', callback_data='change_phone')
    markup.row(item3)
    return markup


# Лэндинг на магазин
def markup_collections():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('RE: BORN', callback_data='re_born')
    item2 = InlineKeyboardButton('CHAOS', callback_data='chaos')
    markup.row(item1, item2)
    item3 = InlineKeyboardButton('Vision of the Future', callback_data='vision_of_the_future')
    markup.row(item3)
    item4 = InlineKeyboardButton('MARS_4', callback_data='mars_4')
    item5 = InlineKeyboardButton('EXHALE', callback_data='exhale')
    markup.row(item4, item5)
    item6 = InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(item6)
    return markup


# Запись на пирсинг
def markup_piercing():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Назад', callback_data='shop')
    item2 = InlineKeyboardButton('Записаться 📅', callback_data='calendar_piercing')
    markup.row(item1, item2)
    item3 = InlineKeyboardButton('Скрыть', callback_data='hide')
    markup.row(item3)
    return markup


# Шаги записи на услугу
# Установка имени клиента
def step_set_first_name(message, bot, call, cal_id):
    first_name = message.text
    # проверяем, является ли имя буквой или словом
    if not first_name.isalpha():
        msg = bot.send_message(message.chat.id, 'Имя должно состоять из букв', reply_to_message_id=message.message_id)
        bot.register_next_step_handler(msg, step_set_first_name, bot, call, cal_id)  # если не буква, и не слово, то
        # перезапускаем эту функцию
    else:
        first_name = first_name.capitalize()  # капитализируем имя
        msg = bot.send_message(call.message.chat.id, 'Ведите фамилию')
        bot.register_next_step_handler(msg, step_set_last_name, bot, call, cal_id, first_name)  # переходим в функцию
        # установки фамилии


# Установка фамилии клиента
def step_set_last_name(message, bot, call, cal_id, first_name):
    last_name = message.text
    # проверяем, является ли фамилия буквой или словом
    if not last_name.isalpha():
        msg = bot.send_message(message.chat.id, 'Фамилия должна состоять из букв',
                               reply_to_message_id=message.message_id)
        bot.register_next_step_handler(msg, step_set_last_name, bot, call, cal_id, first_name)  # если не буква, и не
        # слово, то перезапускаем эту функцию
    else:
        last_name = last_name.capitalize()  # капитализируем фамилию
        msg = bot.send_message(call.message.chat.id, 'Ведите ваш номер телефона в формате "7-123-456-7890" 📲')
        bot.register_next_step_handler(msg, step_set_phone, bot, call, cal_id, first_name, last_name)  # переходим в
        # функцию установки телефона


# Установка номера телефона клиента
def step_set_phone(message, bot, call, cal_id, first_name, last_name):
    global LSTEP
    phone = message.text
    # проверяем, является ли номер корректным
    if not correct_number(phone):
        msg = bot.send_message(message.chat.id, 'Номер телефона должен быть в формате "7-123-456-7890"',
                               reply_to_message_id=message.message_id)
        bot.register_next_step_handler(msg, step_set_phone, bot, call, cal_id, first_name, last_name)  # если
        # неправильный формат, то перезапускаем эту функцию
    else:
        update_client(call.from_user.id, first_name, last_name, phone)  # добавляем клиенту имя, фамилию, телефон
        calendar, step = WYearTelegramCalendar(calendar_id=cal_id, locale='ru',
                                               min_date=date.today()).build()  # формируем календарь
        if cal_id == 1:
            string = 'пирсинг'
        bot.send_message(call.message.chat.id, f'Выберите {LSTEP[step]} записи на {string}', reply_markup=calendar)


# Обработчик календаря записи на услуги
def callback_calendar(bot, call):
    global LSTEP
    cal_id = int(call.data.split('_')[1])
    if cal_id == 1:
        string = 'пирсинг'
    result, key, step = WYearTelegramCalendar(calendar_id=cal_id, locale='ru', min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f'Выберите {LSTEP[step]} записи на {string}',
                              call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        add_booking(call, call.from_user.id, result)
        bot.answer_callback_query(call.id, text='Дата выбрана')
        markup = markup_back_to_landing()
        bot.edit_message_text(f'Вы записаны!\n'
                              f'Ждем вас {result} на {string}', call.message.chat.id, call.message.message_id,
                              reply_markup=markup)


# Обработчик кнопок
def callback_query(bot, call):
    req = call.data
    if req == 'hide':
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif req == 'start':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        handle_start_help(bot, call.message)

    elif req == 'shop':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = markup_shop()
        img_url = 'https://www.freak-butik.ru/photo_content/20.jpg'
        title = 'Загляни в своей профиль или переходи к покупкам'
        bot.send_photo(call.message.chat.id, img_url, caption=title, reply_markup=markup)

    elif req == 'profile':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        try:
            access = get_access(call.message.chat.id)
            if access == 0:
                access_name = 'Клиент'
            elif access == 1:
                access_name = 'Администратор'
            elif access == 777:
                access_name = 'Разработчик'
            profile = view_client(call.message.chat.id)
            markup = markup_profile()
            bot.send_message(call.message.chat.id,
                             f'*📇 | Твой профиль:*\n\n*👤 | Ваш ID:* {profile[0]}\n'
                             f'*💸 | Баланс:* {profile[3]} ₽\n'
                             f'*👑 | Уровень доступа:* {access_name}\n'
                             f'*🛒 | Куплено товаров:* {profile[5]}\n\n'
                             f'*☎ | Телефон:* {profile[8]}\n\n'
                             # f'*🗂 Чтобы посмотреть список купленных товаров напишите /mybuy*'
                             , parse_mode='Markdown', reply_markup=markup)
        except:
            bot.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

    elif req == 'collections':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = markup_collections()
        img_url = 'https://avatars.mds.yandex.net/get-altay/1881820/2a0000016b1e99d5bf098ec3ede3f4d8b5b9/XXXL'
        title = text.collections
        bot.send_photo(call.message.chat.id, img_url, caption=title, parse_mode='Markdown', reply_markup=markup)

    elif (req == 'women') or ('pagination' in req):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        product_id = 1  # TODO: реализовать выбор продукта
        product = get_product(product_id)
        product_id = product[0]
        product_name = product[1]
        product_price = product[2]
        product_url = product[3]
        if req == 'women':
            count = 10  # TODO: сделать зависимым от количества картинок в папке
            page = 1

        elif 'pagination' in req:
            json_string = json.loads(req)
            count = json_string['CountPage']
            page = json_string['NumberPage']

        markup = markup_product(count, page, product_url)
        filepath = os.path.join(os.getcwd(), 'products', str(product_id))
        if not os.path.exists(filepath):
            print("product folder doesn't exist")
        else:
            print("product folder exists")
        img = os.path.join(filepath, 'id_' + str(product_id) + '_' + str(page - 1) + '.jpg')
        title = text.products[0]
        bot.send_photo(call.message.chat.id, photo=open(img, 'rb'),
                       caption=title.format(product_name, product_price, page, count),
                       parse_mode='Markdown', reply_markup=markup)

    elif req == 'book_piercing':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = markup_piercing()
        img_url = 'https://m.freak-butik.ru/img/Small-ALEXA.png'
        title = 'Запишись на пирсинг'
        bot.send_photo(call.message.chat.id, img_url, caption=title, reply_markup=markup)

    elif req == 'calendar_piercing':  # or Сюда можно добавить коллбэки с кнопок других услуг:
        if req == 'calendar_piercing':
            cal_id = 1
        # Сюда можно добавить идентификаторы других услуг
        msg = bot.send_message(call.message.chat.id, 'Ведите имя')
        bot.register_next_step_handler(msg, step_set_first_name, bot, call, cal_id)  # переходим в функцию задания имени
