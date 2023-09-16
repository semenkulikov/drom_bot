import re
from typing import Dict
from random import choice


def get_template(template: str) -> Dict[str, list | str] | None:
    """ Функция для обработки шаблона сообщения """
    try:
        result_dict = dict()
        message, percent = template.split("!")
        result_dict["percent"] = percent
        greeting, verb, noun, text = re.split(r'\[*\]', message)
        greeting = greeting[greeting.index("[") + 1:]
        verb = verb[verb.index("[") + 1:]
        noun = noun[noun.index("[") + 1:]
        result_dict["greetings"] = greeting.split(":")
        result_dict["verbs"] = verb.split(":")
        result_dict["nouns"] = noun.split(":")
        result_dict["message"] = text
        return result_dict
    except Exception:
        return {}


def get_random_message(message_dict: dict) -> str:
    """ Функция для получения рандомного сообщения """
    random_greeting = choice(message_dict.get("greetings"))
    random_verb = choice(message_dict.get("verbs"))
    random_noun = choice(message_dict.get("nouns"))
    random_message = f"{random_greeting} {random_verb} {random_noun} {message_dict.get('message')}"
    return random_message
