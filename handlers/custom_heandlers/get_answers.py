import os
import sys
from time import sleep

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{BASE_DIR}/../")

from handlers.custom_heandlers.work.parser import get_all_messages
from loader import bot

if __name__ == '__main__':
    message_id = sys.argv[1]
    while True:
        messages_list = get_all_messages()
        if len(messages_list) == 0:
            bot.send_message(message_id, "Нет новых сообщений.")
        else:
            bot.send_message(message_id, f"Вот ответы продавцов ({len(messages_list)}):")
            for message in messages_list:
                bot.send_message(message_id, message)
            sleep(10 * 64)

