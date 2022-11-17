import os
from urllib.parse import urljoin
import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from SQLighter import SQLighter


# Функция добавления нового клиента в БД
def add_client(client):
    db_worker = SQLighter(config.database_name)
    res = db_worker.add_client(client)
    db_worker.close()
    if res:  # Если новый клиент был добавлен
        return True
    else:
        return False


def markup_start():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton('Магазин 🛒', callback_data='shop')
    item2 = InlineKeyboardButton('Наш сайт 🕸', url=config.shop_url)
    markup.row(item1, item2)
    item3 = InlineKeyboardButton('Пирсинг 💍', callback_data='book_piercing')
    item4 = InlineKeyboardButton('Контакты 📠', url=urljoin(config.shop_url, '/contact'))
    markup.row(item3, item4)
    return markup


def handle_start_help(bot, message):
    try:
        nick = message.chat.first_name
        user_id = message.chat.id
        chat_id = message.chat.id
        client = (user_id, nick)
        client_added = add_client(client)
        markup = markup_start()
        filepath = os.path.join(os.getcwd(), 'static')
        img = os.path.join(filepath, 'landing.jpg')
        if client_added:  # Если новый клиент был добавлен
            if message.chat.type == 'private':
                bot.send_photo(chat_id, photo=open(img, 'rb'),
                               caption=f'Добро пожаловать, {nick}!\n'
                                       f'Ты попал в бот магазина {config.shop_name} 🛒\n'
                                       f'Отправь /help, чтобы узнать доступные команды', reply_markup=markup)
            else:
                bot.send_photo(chat_id, photo=open(img, 'rb'),
                               caption=f'Добро пожаловать, {message.chat.title}!\n'
                                       f'Ты попал в бот магазина {config.shop_name} 🛒\n'
                                       f'Отправь /help, чтобы узнать доступные команды', reply_markup=markup)
        else:  # Если клиент уже зарегистрирован
            if message.chat.type == 'private':
                bot.send_photo(chat_id, photo=open(img, 'rb'),
                               caption=f'Добро пожаловать, {nick}!\n'
                                       f'Ты попал в бот магазина {config.shop_name} 🛒\n'
                                       f'Ты уже зарегистрирован у нас!\n'
                                       f'Отправь /help, чтобы узнать доступные команды', reply_markup=markup)
            else:
                bot.send_photo(chat_id, photo=open(img, 'rb'),
                               caption=f'Добро пожаловать, {message.chat.title}!\n'
                                       f'Ты попал в бот магазина {config.shop_name} 🛒\n'
                                       f'Ты уже зарегистрирован у нас!\n'
                                       f'Отправь /help, чтобы узнать доступные команды', reply_markup=markup)
    except:
        bot.send_message(message.chat.id, '🚫 | Ошибка при выполнении команды')
