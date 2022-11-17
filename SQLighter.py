# -*- coding: utf-8 -*-
"""
Created on Oct 22, 2017

@author: Administrator
"""
import sqlite3
from datetime import date


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()


    def create_clients(self):
        """ Создаем базу клиентов """
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                                       'user_id INT NOT NULL, nick TEXT, cash INT, access INT,'
                                       'bought INT, first_name TEXT, last_name TEXT, phone TEXT)')


    def create_shop(self):
        """ Создаем магазин """
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS shop (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                       'name TEXT, price INT, url TEXT, '
                                       'whobuy TEXT)')

    def create_piercing(self):
        """ Создаем запись на пирсинг """
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS calendar_piercing (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                                       'user_id INT NOT NULL, nick TEXT, first_name TEXT, last_name TEXT, phone TEXT,'
                                       'year TEXT, month TEXT, day TEXT, booking_date TEXT)')


    def select_all(self, table):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM {}'.format(table)).fetchall()


    def add_client(self, client):
        """ Добавляем нового клиента """
        with self.connection:
            res = self.cursor.execute(f'SELECT id FROM clients WHERE user_id = {client[0]}').fetchone()  # Выбрать клиента по id
            if res is None:  # Если пользователя нет в таблице
                self.cursor.execute('INSERT INTO clients (user_id, nick, cash, access, bought)'
                                           'VALUES (?, ?, 0, 0, 0)', client)  # Добавить нового клиента
                return True
            else:
                return False


    def update_client(self, user_id, first_name, last_name, phone):
        """ Дополняем данные о клиенте """
        with self.connection:
            client_update = (first_name, last_name, phone)
            return self.cursor.execute(f'UPDATE clients SET first_name = ?, last_name = ?,'
                                       f'phone = ? WHERE user_id = {user_id}', client_update)


    def get_access(self, user_id):
        """ Получаем уровень доступа пользователя """
        with self.connection:
            access = self.cursor.execute(f'SELECT * FROM clients WHERE user_id = {user_id}').fetchone()[4]
            return access


    def view_client(self, user_id):
        """ Получаем данные о пользователе """
        with self.connection:
            profile = self.cursor.execute(f'SELECT * FROM clients WHERE user_id = {user_id}').fetchone()
            return profile


    def get_product(self, product_id):
        """ Получаем данные о продукте """
        with self.connection:
            product = self.cursor.execute(f'SELECT * FROM shop WHERE id = {product_id}').fetchone()
            return product


    def add_booking(self, user_id, table, date_booked):
        """ Добавляем запись на услугу в таблицу услуги """
        with self.connection:
            date_booked = date_booked + (date.today(),) # создаем tuple для подстановки даты записи на услугу
            self.cursor.execute(f'INSERT INTO {table} (user_id, nick, first_name, last_name, phone, year, month, day,'
                                f'booking_date) VALUES ((SELECT user_id FROM clients WHERE user_id = {user_id}),'
                                f'(SELECT nick FROM clients WHERE user_id = {user_id}),'
                                f'(SELECT first_name FROM clients WHERE user_id = {user_id}),'
                                f'(SELECT last_name FROM clients WHERE user_id = {user_id}), '
                                f'(SELECT phone FROM clients WHERE user_id = {user_id}),'
                                f' ?, ?, ?, ?)', date_booked)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
