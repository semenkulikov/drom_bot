import datetime
import random
import subprocess
from time import sleep
from fp.fp import FreeProxy
import requests
from lxml import etree
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from config_data.config import DRIVER_PATH, PATH_TO_PYTHON
from database.models import Interval, MailingTime, Proxy
from handlers.custom_heandlers.work.send_message import send_message_to_seller, get_random_account, filter_answer, \
    login_to_drom
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# def filter_answer(text: str) -> bool:
#     """ Функция-фильтр для фильтрации ответов продавцов. """
#     text_lower = text.lower()
#     bad_words_re = r"(\s+|^)[пПnрРp]?[3ЗзВBвПnпрРpPАaAаОoO0о]?[сСcCиИuUОoO0оАaAаыЫуУyтТT]?[Ппn][иИuUeEеЕ][зЗ3][ДдDd]" \
#                    r"\w*[\?\,\.\;\-]*|(\s+|^)[рРpPпПn]?[рРpPоОoO0аАaAзЗ3]?[оОoO0иИuUаАaAcCсСзЗ3тТTуУy]?[XxХх][уУy]" \
#                    r"[йЙеЕeEeяЯ9юЮ]\w*[\?\,\.\;\-]*|(\s+|^)[бпПnБ6][лЛ][яЯ9]([дтДТDT]\w*)?[\?\,\.\;\-]*|(\s+|^)((" \
#                    r"[зЗоОoO03]?[аАaAтТT]?[ъЪ]?)|(\w+[оОOo0еЕeE]))?[еЕeEиИuUёЁ][бБ6пП]([аАaAиИuUуУy]\w*)?[\?\,\.\;\-]*"
#     if re.findall(bad_words_re, text_lower):
#         return False
#
#     for word in DENIAL_WORDS:
#         if word in text_lower:
#             return False
#     return True
#
#
# def login_to_drom(browser):
#     """ Функция для логина на сайте """
#     browser.get("https://my.drom.ru/sign?return=https%3A%2F%2Fwww.drom.ru%2F%3Ftcb%3D1695055100")
#     accounts_obj = []
#     for obj in Account.select().iterator():
#         accounts_obj.append(obj)
#     if accounts_obj is None:
#         return None
#     random_account = random.choice(accounts_obj)
#     try:
#         text_input_login = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH,
#                                             '//*[@id="sign"]'))
#         )
#         text_input_login.send_keys(random_account.login)
#         text_input_password = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH,
#                                             '//*[@id="password"]'))
#         )
#         text_input_password.send_keys(random_account.password)
#
#         button = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH, '//*[@id="signbutton"]'))
#         )
#         button.click()
#         try:
#             try:
#                 result_code = WebDriverWait(browser, 10).until(
#                     EC.presence_of_element_located((By.XPATH,
#                                                     '//*[@id="signForm"]/form/div[2]/button'))
#                 )
#             except Exception:
#                 next_code = WebDriverWait(browser, 10).until(
#                     EC.presence_of_element_located((By.XPATH,
#                                                     '//*[@id="signForm"]/a[2]'))
#                 )
#                 next_code.click()
#                 result_code = WebDriverWait(browser, 10).until(
#                     EC.presence_of_element_located((By.XPATH,
#                                                     '//*[@id="signForm"]/form/div[2]/button'))
#                 )
#             result_code.click()
#             phone = WebDriverWait(browser, 10).until(
#                 EC.presence_of_element_located((By.XPATH,
#                                                 '//*[@id="signForm"]/div/div/div[2]'))
#             )
#
#             code = int(input(f"Введите код, пришедший на номер {phone}"))
#             text_input_code = WebDriverWait(browser, 10).until(
#                 EC.presence_of_element_located((By.XPATH,
#                                                 '//*[@id="code"]'))
#             )
#             text_input_code.send_keys(code)
#             button_code = WebDriverWait(browser, 10).until(
#                 EC.presence_of_element_located((By.XPATH, '//*[@id="signForm"]/form/button'))
#             )
#             button_code.click()
#
#         except Exception:
#             pass
#     except Exception:
#         print(f"Внимание! Неверные логин и пароль: {random_account.login} - {random_account.password}")
#     else:
#         print(f"Авторизация прошла успешно: {random_account.login} - {random_account.password}")
#
#
# def send_message_to_seller(path_to_announcement, id_user):
#     """ Функция для отправки сообщения по объявлению """
#     browser = webdriver.Chrome(service=ChromeService(executable_path=DRIVER_PATH), options=options)
#
#     login_to_drom(browser)
#
#     browser.get(path_to_announcement)
#     try:
#         price = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]'))
#         ).text
#     except Exception:
#         price = None
#     price_norm = int(''.join(price[:-2].split())) if price is not None else None
#     try:
#         announcement_name = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[2]/h1/span"))
#         ).text
#     except Exception:
#         announcement_name = None
#     try:
#         button_phone = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH,
#                                             "/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[5]/button"))
#         )
#         button_phone.click()
#         phone = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH,
#                                             "/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[6]/div[1]/span"))
#         ).text
#     except Exception:
#         phone = None
#     try:
#         send_button = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH,
#                                             '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[6]/div/button/div'
#                                             ))
#         )
#     except Exception:
#         return
#     send_button.click()
#     template_dict = get_template(TEMPLATE_STRING)
#     random_text = get_random_message(template_dict)
#     new_price = price_rounding(price_norm, int(template_dict["percent"]))
#     random_text = random_text.format(price=new_price)
#     # Здесь получение поля
#     text_input_message = WebDriverWait(browser, 10).until(
#         EC.presence_of_element_located((By.XPATH,
#                                         '/html/body/div[6]/div[2]/div/div[3]/textarea'))
#     )
#     text_input_message.send_keys(random_text)
#     send_text_button = WebDriverWait(browser, 10).until(
#         EC.presence_of_element_located((By.XPATH,
#                                         '/html/body/div[6]/div[2]/div/div[3]/button'))
#     )
#     send_text_button.click()
#     # Отправка сообщения селлеру
#
#     # Здесь переход в чат селлера
#     try:
#         html_chat = requests.get("https://my.drom.ru/personal/messaging-modal")
#         html_chat_code = html_chat.text
#         tree = etree.HTML(html_chat_code)
#         dialogs = tree.xpath(
#             '//*[@id="inbox-static-container"]/div/div/section[1]/div/div[2]/div/div[1]/div/div/div[2]/ul'
#         )
#         paths_dialog = []
#         for dialog in dialogs[0]:
#             if dialog.tag == "a":
#                 paths_dialog.append(dialog.get("href"))
#         path_to_dialog = ""
#         for path_dialog in paths_dialog:
#             browser.get(path_dialog)
#             cur_price = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH,
#                                             '//*[@id="inbox-static-container"]/div/div/section[2]/div/section/'
#                                             'div/div[1]/div[2]/div[1]/header/div/h3/strong'))
#         )
#
#             if int(''.join(cur_price.text[:-2].split())) == price_norm:
#                 path_to_dialog = path_dialog
#     except Exception:
#         return
#     try:
#         while True:
#             # Пинг ответа раз в полчаса
#             message_chat = requests.get(path_to_dialog)
#             message_text = message_chat.text
#             tree = etree.HTML(message_text)
#             messages = tree.xpath(
#                 '//*[@id="bzr-dialog-1317610648"]/div'
#             )[0]
#             last_message = []
#             for message in messages:
#                 if message.get("class", "") == "bzr-dialog__msg-container":
#                     last_message.append(message)
#             last_message = last_message[-1]
#             text_message = ""
#             for div_1 in last_message:
#                 if div_1.get("class") == "bzr-dialog__message bzr-dialog__message_out":
#                     for div_2 in div_1:
#                         if div_2.get("class") == "bzr-dialog__message-body":
#                             for div_3 in div_2:
#                                 if div_3.get("class") == "bzr-dialog__body-copy":
#                                     for elem_span in div_3:
#                                         if elem_span.tag == "span":
#                                             text_message = elem_span.text
#
#             answer = text_message if text_message != random_text else ""  # получение чата
#             if answer:  # Если есть новое сообщение
#                 is_good = filter_answer(answer)
#                 if is_good:  # Если сообщение прошло по фильтрам
#                     bot.send_message(id_user, "Внимание! Продавец ответил. Вот информация:\n"
#                                               "Лог переписки:\n"
#                                               f"    Вы - {random_text}\n"
#                                               f"    Продавец - {answer}\n"
#                                               f"Название объявления - {announcement_name}\n"
#                                               f"Ссылка - {path_to_announcement}\n"
#                                               f"Номер телефона - {phone}")
#                 break
#             sleep(60 * 30)
#     except Exception:
#         return
#
#


def get_proxy():
    proxies = [proxy.proxy for proxy in Proxy.select().iterator()]
    proxy = random.choice(proxies) if proxies else None
    return proxy


def get_session(proxy: None):
    # создать HTTP‑сеанс
    session = requests.Session()
    if proxy is not None:
        session.proxies = {"http": proxy, "https": proxy}
    return session


def get_all_messages():
    try:
        """ Здесь будет парсинг последних сообщений продавцов. """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        random_account = get_random_account()
        try:
            proxy = random.choice([proxy.proxy for proxy in Proxy.select().where(Proxy.account == random_account)])
        except Exception:
            proxy = None
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        browser = webdriver.Chrome(service=ChromeService(executable_path=DRIVER_PATH), options=options)
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        browser.execute_cdp_cmd('Network.setUserAgentOverride',
                                {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                              'like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        login_to_drom(browser, random_account)
        browser.get("https://my.drom.ru/personal/messaging-modal")
        messages_list = list()
        for index in range(1, 100):
            try:
                elem = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[1]/div/div[2]/div/div[1]'
                                   f'/div/div/div[2]/ul/li[{index}]'))
                )
                elem.click()
                try:
                    # if answer:  # Если есть новое сообщение
                    #     is_good = filter_answer(answer)
                    #     if is_good:  # Если сообщение прошло по фильтрам
                    #         Answer.create(text="\nВнимание! Продавец ответил. Вот информация:\n"
                    #                            "Лог переписки:\n"
                    #                            f"    Вы - {random_text}\n"
                    #                            f"    Продавец - {answer}\n"
                    #                            f"Название объявления - {announcement_name}\n"
                    #                            f"Ссылка - {path_to_announcement}\n"
                    #                            f"Номер телефона - {phone}")
                    announcement_name_obj = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]/div/section/div/div[1]'
                                   f'/div[2]/div[1]/header/div/h3/a'))
                )
                    announcement_name = announcement_name_obj.text
                    path_to_announcement = announcement_name_obj.get_attribute('href')

                    seller_obj = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]/div/section/'
                                   f'div/div[1]/div[2]/div[1]/header/div/h2/strong/span/a'))
                )
                    seller_login = seller_obj.text
                    seller_path = seller_obj.get_attribute('href')

                    price = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]'
                                   f'/div/section/div/div[1]/div[2]/div[1]/header/div/h3/strong'))
                ).text

                    messages: str = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]'))
                ).text
                    messages = messages[messages.find("р.") + 2:]
                    # Здесь посмотреть как извлечь из этого объекта логи
                    result_text = f"\nПродавец {seller_login} ответил.\n" \
                                  f"Ссылка до страницы продавца - {seller_path}\n" \
                                  f"Имя объявления: {announcement_name}\n" \
                                  f"Ссылка на объявление: {path_to_announcement}\n" \
                                  f"Цена: {price}\n" \
                                  f"Логи переписки:\n{messages}"
                    messages_list.append(result_text)

                except Exception:
                    print("Непредвиденная ошибка! Не получилось спарсить объявление")
            except Exception:
                # Значит кончились диалоги \ либо он один
                break
        if not messages_list:
            # Пробуем один диалог (если список сообщений пустой)
            try:
                elem = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="inbox-static-container"]/div/div/section[1]/div/div[2]/div/div[1]/div/div/div[2]/ul/li'))
                )

                elem.click()
                announcement_name_obj = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]/div/section/div/div[1]'
                                   f'/div[2]/div[1]/header/div/h3/a'))
                )
                announcement_name = announcement_name_obj.text
                path_to_announcement = announcement_name_obj.get("href", None)

                seller_obj = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]/div/section/'
                                   f'div/div[1]/div[2]/div[1]/header/div/h2/strong/span/a'))
                )
                seller_login = seller_obj.text
                seller_path = seller_obj.get("href", None)

                price = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]'
                                   f'/div/section/div/div[1]/div[2]/div[1]/header/div/h3/strong'))
                ).text

                messages: str = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="inbox-static-container"]/div/div/section[2]'))
                ).text
                messages = messages[messages.find("р.") + 2:]
                # Здесь посмотреть как извлечь из этого объекта логи
                result_text = f"\nПродавец {seller_login} ответил.\n" \
                              f"Ссылка до страницы продавца - {seller_path}\n" \
                              f"Имя объявления: {announcement_name}\n" \
                              f"Ссылка на объявление: {path_to_announcement}\n" \
                              f"Цена: {price}\n" \
                              f"Логи переписки:\n{messages}"
                messages_list.append(result_text)

            except Exception:
                messages_list.append("Нет полученных ответов...")
        browser.close()
        return messages_list

    except Exception:
        return ["У вас проблемы с интернетом!"]


def send_messages_drom(url_path, id_user):
    """ Функция для работы в дром. Запускает браузер, переходит по ссылке и рассылает сообщения. """
    # Здесь парсинг ссылок на объявления
    proxy = get_proxy()
    session = get_session(proxy)
    html = session.get(url_path)
    html_code = html.text
    tree = etree.HTML(html_code)
    elem = tree.xpath("/html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]")[0]
    paths = list()
    for a in elem:
        if a.tag == "a":
            is_block = False
            for div in a:
                if div.tag == "div" and div.get("class") == "css-1dkhqyq e1f2m3x80":
                    for div_i in div:
                        if div_i.tag == "div":
                            divs = [div_j for div_j in div_i if div_j.tag == "div"]
                            if len(divs) == 2:
                                is_block = True
                            break
                    break
            if not is_block:
                paths.append(a.get("href"))

    interval_obj = Interval.get_or_none(id=1)
    interval = interval_obj.interval if interval_obj is not None else None
    time = MailingTime.get_or_none(id=1)
    if time is not None:
        start_time, end_time = time.start_time, time.end_time
    else:
        start_time, end_time = None, None

    cur_time = datetime.datetime.now().time()
    if interval is None:
        interval = 1

    while True:
        if start_time is not None and end_time is not None:
            if cur_time < start_time or cur_time > end_time:
                print("Рассылка временно приостановлена, не вкладывается в тайминг.")
                sleep(60 * 60)
                continue

        for path in paths:
            # subprocess.Popen(f"{PATH_TO_PYTHON} handlers/custom_heandlers/work/send_message.py {path} {id_user}",
            #                  close_fds=True)
            send_message_to_seller(path, id_user)
            print(f"Сообщение отправлено, сплю {interval} минут")
            sleep(interval * 60)
        break
