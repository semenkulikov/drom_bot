import datetime
import random
import subprocess
from time import sleep

import psutil
from telebot.types import Message
from handlers.custom_heandlers.work.get_template import get_template, get_random_message
from handlers.custom_heandlers.work.parser import send_messages_drom, get_all_messages
from keyboards.inline.settings import settings_inline
from keyboards.inline.accounts import account_markup, get_actions_acc, get_proxy_markup
from loader import bot
from states.states import UrlState, GetSettingsState, AccountState, UpdateAccount
from urllib.parse import urlparse
from config_data.config import TEMPLATE_STRING, PATH_TO_PYTHON, BASE_DIR
from database.models import Interval, MailingTime, Account, Proxy, Answer


PIDS_PROCESS = list()


@bot.message_handler(commands=["url"])
def get_command_url(message: Message) -> None:
    """ Хендлер, ловит команду url """
    bot.send_message(message.from_user.id,
                     "Хорошо, введите ссылку на страницу, откуда мне брать объявления для рассылки")
    bot.set_state(message.from_user.id, UrlState.get_url)


@bot.message_handler(state=UrlState.get_url)
def get_url(message: Message) -> None:
    """ Хендлер для получения ссылки """
    global PIDS_PROCESS

    url = message.text
    print(url)
    if not urlparse(url).scheme:
        bot.send_message(message.from_user.id, "Необходимо ввести корректную ссылку.")
        return
    # Здесь сохранение ссылки в бд и рассылка сообщений. Вызывается функция для запросов к апи.
    bot.send_message(message.from_user.id, "Ссылка сохранена успешно. Началась рассылка сообщений...")
    bot.set_state(message.from_user.id, None)
    process = subprocess.Popen(f"{PATH_TO_PYTHON} "
                     f"{BASE_DIR}/handlers/custom_heandlers/work/parser.py {url} {message.from_user.id}",
                     close_fds=True)
    PIDS_PROCESS.append(process.pid)


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
        bot.send_message(call.message.chat.id, 'Хорошо, напишите промежуток интервала вида min - min (5 - 15).')
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
        proxies = " ".join([proxy.proxy for proxy in Proxy.select().where(Proxy.account == account)])
        if proxies == "":
            proxies = "нет прокси в базе данных"
        accounts_text += f"\n{account.login}: {account.password} ({proxies})"
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
                                           f"\nНовый аккаунт внесен в базу данных.\n"
                                           f"Если хотите, можно привязать прокси для этого аккаунта.\n"
                                           f"Вида: http(s)://username:password@proxyurl:proxyport\n"
                                           f"Http или https пишите исходя из прокси.\n"
                                           f"Для пропуска введите -.")

    bot.set_state(message.from_user.id, AccountState.get_proxy)


@bot.message_handler(state=AccountState.get_proxy)
def get_proxy(message: Message) -> None:

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_dict:
        login = data_dict["login"]

    if message.text == "-":
        bot.send_message(message.from_user.id, "Хорошо, прокси не привязан.")

    else:
        if "@" not in message.text or "http" not in message.text:
            bot.send_message(message.from_user.id, "Некорректно введен прокси!")
            return
        account_obj = Account.get(Account.login == login)
        try:
            proxy_obj = Proxy.get(Proxy.proxy == message.text)
        except Exception:
            proxy_obj = Proxy.create(
                proxy=message.text,
                account=account_obj
            )
        account_obj.save()
        bot.send_message(message.from_user.id, f"Прокси {message.text} сохранен.")
    bot.set_state(message.from_user.id, None)


@bot.message_handler(commands=["update"])
def update_accounts(message: Message) -> None:
    bot.send_message(message.from_user.id, "Выберите аккаунт для редактирования, нажав на кнопку.",
                     reply_markup=account_markup())
    bot.set_state(message.from_user.id, UpdateAccount.get_acc)


@bot.callback_query_handler(func=None, state=UpdateAccount.get_acc)
def get_acc(call) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data_dict:
        data_dict["cur_id"] = call.data
    cur_account: Account = Account.get_by_id(call.data)
    proxies = ", ".join([proxy.proxy for proxy in Proxy.select().where(Proxy.account == cur_account)])
    if proxies == "":
        proxies = "нет прокси"
    bot.send_message(call.message.chat.id, f"Текущий аккаунт: {cur_account.login} - {cur_account.password} - {proxies}")
    bot.send_message(call.message.chat.id, "Выберите, что редактировать", reply_markup=get_actions_acc())
    bot.set_state(call.message.chat.id, UpdateAccount.get_info)


@bot.callback_query_handler(func=None, state=UpdateAccount.get_info)
def get_info_acc(call) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data_dict:
        acc_id = data_dict["cur_id"]
    cur_account = Account.get_by_id(acc_id)
    proxies = ", ".join([proxy.proxy for proxy in Proxy.select().where(Proxy.account == cur_account)])
    if call.data == "1":
        # Login
        bot.send_message(call.message.chat.id, "Хорошо, введите новый логин")
        bot.set_state(call.message.chat.id, UpdateAccount.update_login)
    elif call.data == "2":
        # Pass
        bot.send_message(call.message.chat.id, "Ок, введите новый пароль")
        bot.set_state(call.message.chat.id, UpdateAccount.update_pass)
    elif call.data == "3":
        if proxies == '':
            bot.send_message(call.message.chat.id, "Введите прокси для добавления к этому аккаунту.")
            bot.set_state(call.message.chat.id, UpdateAccount.update_proxy)
        # Proxy
        else:
            bot.send_message(call.message.chat.id, "Выберите прокси для редактирования, нажав на кнопку.",
                             reply_markup=get_proxy_markup(acc_id))
            bot.set_state(call.message.chat.id, UpdateAccount.update_proxy_one)


@bot.message_handler(state=UpdateAccount.update_login)
def update_login(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_dict:
        acc_id = data_dict["cur_id"]
    cur_account: Account = Account.get_by_id(acc_id)
    cur_account.login = message.text
    cur_account.save()
    bot.send_message(message.chat.id, f"Текущий логин: {message.text}. Логин успешно сохранен.")
    bot.set_state(message.chat.id, None)


@bot.message_handler(state=UpdateAccount.update_pass)
def update_pass(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_dict:
        acc_id = data_dict["cur_id"]
    cur_account: Account = Account.get_by_id(acc_id)
    cur_account.password = message.text
    cur_account.save()
    bot.send_message(message.chat.id, f"Текущий пароль: {message.text}. Пароль успешно сохранен.")
    bot.set_state(message.chat.id, None)


@bot.callback_query_handler(func=None, state=UpdateAccount.update_proxy_one)
def update_proxy(call) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data_dict:
        data_dict["cur_proxy_id"] = call.data
    bot.send_message(call.message.chat.id, f"Окей, введите новый прокси или - для удаления текущего.")
    bot.set_state(call.message.chat.id, UpdateAccount.update_proxy)


@bot.message_handler(state=UpdateAccount.update_proxy)
def update_proxy_2(message: Message) -> None:
    with bot.retrieve_data(message.chat.id, message.chat.id) as data_dict:
        acc_id = data_dict.get("cur_id")
        cur_proxy_id = data_dict.get("cur_proxy_id", None)
    if cur_proxy_id is None:
        if "@" not in message.text or "http" not in message.text:
            bot.send_message(message.chat.id, f"Введенный прокси некорректен. Введите еще раз.")
            return
        Proxy.create(proxy=message.text, account=acc_id)
        bot.send_message(message.chat.id, f"Прокси {message.text} успешно добавлен к аккаунту.")
        bot.set_state(message.chat.id, None)
        return
    cur_proxy: Proxy = Proxy.get_by_id(cur_proxy_id)

    if message.text == "-":
        bot.send_message(message.chat.id, f"Хорошо, прокси {cur_proxy.proxy} удален.")
        cur_proxy.delete_instance()
    else:
        bot.send_message(message.chat.id, f"Хорошо, прокси {cur_proxy.proxy} изменен на прокси {message.text}")
        cur_proxy.proxy = message.text
        cur_proxy.save()

    bot.set_state(message.chat.id, None)


@bot.message_handler(commands=["info"])
def get_info(message: Message) -> None:
    """ Обработчик команды для выдачи основной информации """

    # Здесь достаю интервал из бд.
    interval_obj = Interval.get_or_none(id=1)
    interval = interval_obj.interval if interval_obj is not None else ""
    start_i, stop_i = interval.split("-")
    start_i, stop_i = int(start_i.strip()), int(stop_i.strip())
    minutes = [min_i for min_i in range(start_i, stop_i + 1)]
    print(minutes)
    random_interval = random.choice(minutes)
    time = MailingTime.get_or_none(id=1)
    if time is not None:
        start_time, end_time = time.start_time, time.end_time
    else:
        start_time, end_time = None, None

    # Здесь достаю акки из бд.
    accounts_obj = Account.select()
    accounts_text = ""
    for account in accounts_obj:
        proxies = " ".join([proxy.proxy for proxy in Proxy.select().where(Proxy.account == account)])
        if proxies == "":
            proxies = "нет прокси в базе данных"
        accounts_text += f"\n        {account.login}: {account.password} ({proxies})"
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
                  f"Рандомный интервал: {random_interval}\n    " \
                  f"Время начала рассылки: {start_time}\n    " \
                  f"Время окончания: {end_time}\n    " \
                  f"Ваши текущие аккаунты: {accounts_text}\n    " \
                  f"Шаблон сообщения: {template_text}\n    " \
                  f"Процент понижения цены: {template_dict.get('percent')}\n    " \
                  f"Рандомное сообщение: \n{random_text}"
    bot.send_message(message.from_user.id, result_text)


@bot.message_handler(commands=["get"])
def get_answer(message: Message) -> None:
    """ Обработчик команды для выдачи ответов продавцов """
    bot.send_message(message.from_user.id, "Подождите, начался парсинг ответов...")
    bot.send_message(message.from_user.id, "Буду присылать вам ответы раз в 10 минут")
    while True:
        messages_list = get_all_messages()

        bot.send_message(message.from_user.id, f"Вот ответы продавцов ({len(messages_list)}):")
        bot.send_message(message.from_user.id, "\n".join(messages_list))
        sleep(10 * 64)


@bot.message_handler(commands=["stop"])
def stopping_bot(message: Message) -> None:
    """ Обработчик команды для остановки рассылки сообщений """
    bot.send_message(message.from_user.id, "Подождите, останавливаю рассылку...")
    global PIDS_PROCESS

    # bot.stop_bot()
    PROCNAMES = [
        "chrome.exe",
    ]

    for proc in psutil.process_iter():
        # check whether the process name matches
        # if proc.name() in PROCNAMES:
        #     proc.kill()
        if proc.pid in PIDS_PROCESS:
            proc.kill()
            PIDS_PROCESS.remove(proc.pid)

    bot.send_message(message.from_user.id, "Готово!")
