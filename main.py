from loader import bot
import handlers  # noqa
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
from database.models import create_models, delete_answers

if __name__ == '__main__':
    create_models()
    delete_answers()
    print("Подключение к базе данных...")
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    print("Загрузка базовых команд...")
    print("Бот запущен.")
    bot.remove_webhook()
    bot.infinity_polling(timeout=60 * 60)
