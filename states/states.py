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
