from telebot.handler_backends import State, StatesGroup


class UrlState(StatesGroup):
    get_url = State()


class GetSettingsState(StatesGroup):
    get_settings = State()
    time = State()
    interval = State()


class AccountState(StatesGroup):
    get_login = State()
    get_pass = State()
    get_proxy = State()


class UpdateAccount(StatesGroup):
    get_acc = State()
    get_info = State()
    update_login = State()
    update_pass = State()
    update_proxy_one = State()
    update_proxy = State()
