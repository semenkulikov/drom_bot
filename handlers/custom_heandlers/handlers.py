import datetime
from telebot.types import Message
from handlers.custom_heandlers.work.get_template import get_template, get_random_message
from keyboards.inline.settings import settings_inline
from loader import bot
from states.states import UrlState, GetSettingsState, AccountState
from urllib.parse import urlparse
from config_data.config import TEMPLATE_STRING


@bot.message_handler(commands=["url"])
def get_command_url(message: Message) -> None:
    """ Хендлер, ловит команду url """
    bot.send_message(message.from_user.id,
                     "Хорошо, введите ссылку на страницу, откуда мне брать объявления для рассылки")
    bot.set_state(message.from_user.id, UrlState.get_url)


@bot.message_handler(state=UrlState.get_url)
def get_url(message: Message) -> None:
    """ Хендлер для получения ссылки """

    url = message.text
    if not urlparse(url).scheme:
        bot.send_message(message.from_user.id, "Необходимо ввести корректную ссылку.")
        return
    # Здесь сохранение ссылки в бд и рассылка сообщений. Вызывается функция для запросов к апи.
    # Наверное, нет смысла сохранять ссылку в бд, если она нужна только для получения объявлений.
    bot.send_message(message.from_user.id, "Ссылка сохранена успешно. Началась рассылка сообщений...")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(commands=["settings"])
def get_settings(message: Message) -> None:
    """ Хендлер для настроек рассылки """
    interval, time = 0, 0
    # Здесь достаю интервал и тайминг из бд
    bot.send_message(message.from_user.id, f"Текущий интервал рассылки: {interval}\nТекущий тайминг: {time}")
    bot.send_message(message.from_user.id,
                     "Что настраивать? Выберите одну кнопку", reply_markup=settings_inline())
    bot.set_state(message.from_user.id, GetSettingsState.get_settings)


@bot.callback_query_handler(func=None, state=GetSettingsState.get_settings)
def interval_or_time(call):
    if call.data == "interval":
        bot.send_message(call.message.chat.id, 'Хорошо, введите время между отправкой сообщений (в минутах).')
        bot.set_state(call.message.chat.id, GetSettingsState.interval)
    elif call.data == "time":
        bot.send_message(call.message.chat.id, "Напишите время рассылки в формате: h:m - h:m (12:00 - 20:00)")
        bot.set_state(call.message.chat.id, GetSettingsState.time)


@bot.message_handler(state=GetSettingsState.interval)
def interval_state(message: Message) -> None:
    """ Хендлер для получения интервала """
    interval = message.text
    # Здесь сохранение интервала в бд.
    bot.send_message(message.from_user.id, f"Интервал {interval} успешно сохранен в базу данных.")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(state=GetSettingsState.time)
def time_state(message: Message) -> None:
    """ Хендлер для получения времени рассылки """

    time = message.text
    try:
        start_time, end_time = time.split(" - ")
        start_time, end_time = start_time.split(":"), end_time.split(":")
        start_time = datetime.time(hour=int(start_time[0]), minute=int(start_time[1]))
        end_time = datetime.time(hour=int(end_time[0]), minute=int(end_time[1]))
    except Exception:
        bot.send_message(message.from_user.id, "Необходимо ввести время в формате h:m - h:m (12:00 - 20:00)")
        return
    # Здесь сохранение тайминга в бд.
    bot.send_message(message.from_user.id, "Тайминг успешно сохранен в базу данных.")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(commands=["accounts"])
def get_account(message: Message) -> None:
    """ Обработчик для получения нового аккаунта """
    # Здесь достаю акки из бд.
    accounts_text = ""
    for account in []:
        accounts_text += f"\n{account.login}: {account.password}"
    if accounts_text == "":
        accounts_text = "\nУ вас нет сохраненных аккаунтов."
    bot.send_message(message.from_user.id, f"Ваши текущие аккаунты: {accounts_text}")
    bot.send_message(message.from_user.id, "Введите логин / почту / телефон.")
    bot.set_state(message.from_user.id, AccountState.get_login)


@bot.message_handler(state=AccountState.get_login)
def get_login(message: Message) -> None:
    """ Хендлер для получения логина """

    login = message.text
    # Здесь запоминаю логин аккаунта

    bot.send_message(message.from_user.id, f"Хорошо, логин {login} сохранен. Теперь введите пароль от аккаунта")
    bot.set_state(message.from_user.id, AccountState.get_pass)


@bot.message_handler(state=AccountState.get_pass)
def get_login(message: Message) -> None:
    """ Хендлер для получения пароля """

    password = message.text
    # Здесь запоминаю логин аккаунта

    bot.send_message(message.from_user.id, f"Отлично! Текущий пароль: {password}.\nНовый аккаунт внесен в базу данных.")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(commands=["info"])
def get_info(message: Message) -> None:
    """ Обработчик команды для выдачи основной информации """

    # Здесь достаю интервал из бд.
    interval = 0

    # Здесь тайминг
    start_time, end_time = datetime.time(), datetime.time()

    # Здесь достаю акки из бд.
    accounts_text = ""
    for account in []:
        accounts_text += f"\n        {account.login}: {account.password}"
    if accounts_text == "":
        accounts_text = "\n        У вас нет сохраненных аккаунтов."

    template_dict = get_template(TEMPLATE_STRING)
    template_text = "\n\n{greetings}; {verbs}; {nouns}; {message}\n\n".format(
        greetings=" / ".join(template_dict.get("greetings")),
        verbs=" / ".join(template_dict.get("verbs")),
        nouns=" / ".join(template_dict.get("nouns")),
        message=template_dict.get("message")
    )
    random_text = get_random_message(template_dict)
    result_text = f"Основная информация по боту:\n    Текущий интервал между рассылкой: {interval}\n    " \
                  f"Время начала рассылки: {start_time}\n    " \
                  f"Время окончания: {end_time}\n    " \
                  f"Ваши текущие аккаунты: {accounts_text}\n    " \
                  f"Шаблон сообщения: {template_text}\n    " \
                  f"Процент понижения цены: {template_dict.get('percent')}\n    " \
                  f"Рандомное сообщение: \n{random_text}"
    bot.send_message(message.from_user.id, result_text)
