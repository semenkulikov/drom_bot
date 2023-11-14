from telebot.types import Message
from loader import bot
from config_data.config import ALLOWED_USERS


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния

@bot.message_handler(state=None)
def bot_echo(message: Message):
    if message.from_user.id in ALLOWED_USERS:
        bot.reply_to(message, f"Введите любую команду из меню, чтобы я начал работать\n"
                              f"Либо выберите одну из кнопок, которые я вам прислал")

