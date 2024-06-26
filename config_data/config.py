import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены, т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('url', "Ввести ссылку"),
    ('settings', "Настройка рассылки"),
    ('accounts', "Добавить аккаунт"),
    ('info', "Информация о настройках"),
    ('get', "Получить ответы продавцов"),
    ("get_stop", "Остановить парсинг ответов"),
    ("get_settings", "Настройка get"),
    ("update", "Редактирование аккаунтов"),
    ("start_spam", "Запустить рассылку сообщений"),
    ("stop_spam", "Остановить рассылку сообщений"),
    ("stop", "Выход из всех состояний бота")
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_TO_TEMPLATE = os.path.join(BASE_DIR, "message_template.txt")

DRIVER_PATH = "C:/chromedriver/chromedriver.exe"

ALLOWED_USERS = [
    5194842887,  # Мой
    146012477,   # Deny Devito
]

USERS_SPAM = [
    1893836348,
]

PATH_TO_PYTHON = os.path.normpath(os.path.join(BASE_DIR, "venv/Scripts/python.exe"))

DENIAL_WORDS = [
                # Здесь слова, которые не должны встречаться в ответах продавцов.
                "нет",
                "не согласен",
                "к сожалению",
                "я против",
                "против",
                "не надо",
                "зачем",
                "неинтересно",
                "не интересно",
                "до свидания",
                "не хочу"]


with open(PATH_TO_TEMPLATE, encoding="utf8") as file:
    TEMPLATE_STRING = file.read()
