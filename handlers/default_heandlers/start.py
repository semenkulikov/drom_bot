from sqlite3 import IntegrityError
from config_data.config import ALLOWED_USERS, USERS_SPAM
from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    if message.chat.type == "private":
        if message.from_user.id in ALLOWED_USERS:
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
        else:
            print(f"Внимание! Новый юзер: {message.from_user.full_name} - {message.from_user.id}")
            if message.from_user.id not in USERS_SPAM:
                print(f"Добавляю его к списку пользователей для спама - {USERS_SPAM}")
                USERS_SPAM.append(message.from_user.id)
            else:
                print(f"Пользователь {message.from_user.id} уже есть в списке пользователей для спама")
            bot.send_message(message.from_user.id, f"Здравствуйте, {message.from_user.full_name}! "
                                                   f"Я - телеграм бот. "
                                                   f"Для получения доступа к моим командам обратитесь к администраторам"
                             )
    else:
        print(f"Внимамание! Новая группа: {message.chat.title} - {message.chat.id}")
        bot.send_message(message.chat.id, "Здравствуйте! Я - телеграм бот, модератор каналов и групп. "
                                          "Чтобы получить больше информации, "
                                          "обратитесь к администратору.")


