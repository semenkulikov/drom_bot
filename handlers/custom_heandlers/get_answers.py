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

        bot.send_message(message_id, f"Вот ответы продавцов ({len(messages_list)}):")
        bot.send_message(message_id, "\n".join(messages_list))
        sleep(10 * 64)

