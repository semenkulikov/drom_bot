import datetime
from telebot.types import Message
from handlers.custom_heandlers.work.get_template import get_template, get_random_message
from keyboards.inline.settings import settings_inline
from loader import bot
from states.states import UrlState, GetSettingsState, AccountState
from urllib.parse import urlparse
from config_data.config import TEMPLATE_STRING
from database.models import Interval, MailingTime, Account


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
    print(url)
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
    interval_obj = Interval.get_or_none(id=1)
    interval = interval_obj.interval if interval_obj is not None else None
    time = MailingTime.get_or_none(id=1)
    if time is not None:
        start_time, end_time = time.start_time, time.end_time
    else:
        start_time, end_time = None, None
    bot.send_message(message.from_user.id, f"Текущий интервал рассылки: {interval}"
                                           f"\nТекущий тайминг: {start_time} - {end_time}")
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
    print(interval)
    try:
        interval_obj = Interval.get(id=1)
        interval_obj.interval = interval
        interval_obj.save()
    except Exception:
        Interval.create(interval=interval)
    bot.send_message(message.from_user.id, f"Интервал {interval} успешно сохранен в базу данных.")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(state=GetSettingsState.time)
def time_state(message: Message) -> None:
    """ Хендлер для получения времени рассылки """

    time = message.text
    print(time)
    try:
        start_time, end_time = time.split(" - ")
        start_time, end_time = start_time.split(":"), end_time.split(":")
        start_time = datetime.time(hour=int(start_time[0]), minute=int(start_time[1]))
        end_time = datetime.time(hour=int(end_time[0]), minute=int(end_time[1]))
    except Exception:
        bot.send_message(message.from_user.id, "Необходимо ввести время в формате h:m - h:m (12:00 - 20:00)")
        return
    # Здесь сохранение тайминга в бд.
    try:
        time_obj = MailingTime.get(id=1)
        time_obj.start_time = start_time
        time_obj.end_time = end_time
        time_obj.save()
    except Exception:
        MailingTime.create(start_time=start_time, end_time=end_time)
    bot.send_message(message.from_user.id, "Тайминг успешно сохранен в базу данных.")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(commands=["accounts"])
def get_account(message: Message) -> None:
    """ Обработчик для получения нового аккаунта """
    # Здесь достаю акки из бд.
    accounts_obj = Account.select()
    accounts_text = ""
    for account in accounts_obj:
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
    print(login)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_dict:
        data_dict["login"] = login

    if Account.get_or_none(Account.login == login) is not None:
        bot.send_message(message.from_user.id, f"Аккаунт с таким логином уже существует. "
                                               f"Введите новый пароль для обновления старого")
    else:
        bot.send_message(message.from_user.id, f"Хорошо, логин {login} сохранен. Теперь введите пароль от аккаунта")
    bot.set_state(message.from_user.id, AccountState.get_pass)


@bot.message_handler(state=AccountState.get_pass)
def get_password(message: Message) -> None:
    """ Хендлер для получения пароля """

    password = message.text
    print(password)
    # Здесь запоминаю пароль аккаунта
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_dict:
        login = data_dict["login"]

    try:
        account_obj = Account.get(Account.login == login)
        account_obj.password = password
        account_obj.save()
    except Exception:
        Account.create(
            login=login,
            password=password
        )

    bot.send_message(message.from_user.id, f"Отлично! Текущий пароль: {password}."
                                           f"\nНовый аккаунт внесен в базу данных.")

    bot.set_state(message.from_user.id, None)


@bot.message_handler(commands=["info"])
def get_info(message: Message) -> None:
    """ Обработчик команды для выдачи основной информации """

    # Здесь достаю интервал из бд.
    interval_obj = Interval.get_or_none(id=1)
    interval = interval_obj.interval if interval_obj is not None else None
    time = MailingTime.get_or_none(id=1)
    if time is not None:
        start_time, end_time = time.start_time, time.end_time
    else:
        start_time, end_time = None, None

    # Здесь достаю акки из бд.
    accounts_obj = Account.select()
    accounts_text = ""
    for account in accounts_obj:
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
