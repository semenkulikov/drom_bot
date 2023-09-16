from sqlite3 import IntegrityError

from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.send_message(message.from_user.id, f"""
    Привет, {message.from_user.full_name}! Я - бот для рассылки сообщений в Дром.
Что я умею:

0. Логиниться на платформе под разными акками

1. Переходить по ссылке и рассылать сообщения продавцам. (От разных аккаунтов)

2. Отслеживаю ответивших продавцов по фильтрам

3. Сохраняю следующую информацию:
    a) Лог переписки
    b) Название обьявления
    c) Ссылка на обьявление
    d) Номер телефона (по возможности)

4. Периодически меняю прокси
    
Чтобы узнать все мои команды, введите /help
    """)
