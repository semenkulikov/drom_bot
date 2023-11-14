from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Account, Proxy


def account_markup():
    """ Inline buttons для выбора аккаунта """
    accounts_obj = Account.select()
    actions = InlineKeyboardMarkup(row_width=2)

    for account in accounts_obj:
        actions.add(InlineKeyboardButton(text=f"{account.login}", callback_data=account.id))

    return actions


def get_actions_acc():
    actions = InlineKeyboardMarkup(row_width=2)
    actions.add(InlineKeyboardButton(text=f"Логин", callback_data="1"))
    actions.add(InlineKeyboardButton(text=f"Пароль", callback_data="2"))
    actions.add(InlineKeyboardButton(text=f"Прокси", callback_data="3"))
    actions.add(InlineKeyboardButton(text=f"Вообще удалить его", callback_data="4"))

    return actions


def get_proxy_markup(acc_id):
    actions = InlineKeyboardMarkup(row_width=2)
    for proxy in Proxy.select().where(Proxy.account == acc_id):
        actions.add(InlineKeyboardButton(text=f"{proxy.proxy}", callback_data=proxy.id))
    return actions
