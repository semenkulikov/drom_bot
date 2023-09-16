from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def settings_inline():
    """ Inline buttons для настройки рассылки """
    actions = InlineKeyboardMarkup(row_width=2)
    actions.add(InlineKeyboardButton(text="Настроить интервал рассылки", callback_data="interval"))
    actions.add(InlineKeyboardButton(text="Настроить время рассылки", callback_data="time"))

    return actions
