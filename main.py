# -*- coding: utf-8 -*-
"""
Created on Oct 20, 2022

@author:
"""
import os
import telebot
from flask import Flask, request
from telegram_bot_calendar import WYearTelegramCalendar
import config
# import logging
from SimpleQIWI import *

# bot plugins
import start
import shop_plugin

commands = {  # command description used in the "help" command
    'start': 'Познакомьтесь с ботом',
    'help': 'Список доступных команд',
}


# включение отображения лога в консоли
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console


# telebot.apihelper.proxy = {
#   'https':'socks5://{}:{}'.format(config.ip,config.port)
# }


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for message in messages:
        if message.content_type == 'text':
            # print the sent message to the console
            if message.chat.type == 'private':
                if message.chat.username:
                    print(message.chat.username + " [" + str(message.chat.id) + "]: " + message.text)
                else:
                    print(message.chat.first_name + " [" + str(message.chat.id) + "]: " + message.text)
            else:
                print(message.chat.title + " [" + str(message.chat.id) + "]: " + message.text)


bot = telebot.TeleBot(config.token)
server = Flask(__name__)
bot.set_update_listener(listener)  # register listener

# qiwi = QApi(token='tokenqiwi', phone='phoneqiwi')


# handle the "/start" command
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    start.handle_start_help(bot, message)


# help page
@bot.message_handler(commands=['help'])
def command_help(message):
    help_text = "Доступны следующие команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)  # send the generated help page


# календарь для записи на пирсинг
@bot.callback_query_handler(WYearTelegramCalendar.func(calendar_id=1))
def handle_calendar(call):
    shop_plugin.callback_calendar(bot, call)


# обработчик Inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_button(call):
    shop_plugin.callback_query(bot, call)
    bot.answer_callback_query(call.id)


# redirecting messages from Flask server to the bot
@server.route(f'/{config.token}', methods=['POST'])
def redirect_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


# remove existing webhook and set a new one
# run Flask server
if __name__ == '__main__':
    # bot.infinity_polling()
    bot.remove_webhook()
    bot.set_webhook(url=config.app_url)
    server.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
