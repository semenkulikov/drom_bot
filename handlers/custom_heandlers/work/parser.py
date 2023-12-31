import datetime
import os
import random
import re
import sys
from time import sleep

import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{BASE_DIR}/../../")

from config_data.config import DRIVER_PATH, TEMPLATE_STRING, DENIAL_WORDS
from database.models import Account, Proxy, Answer
from database.models import Interval, MailingTime
from handlers.custom_heandlers.work.get_template import price_rounding, get_template, get_random_message

options = Options()
# options.add_argument("--headless")
# options.add_argument("--incognito")
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
cursor_script = '''
var cursor = document.createElement('div');
cursor.style.position = 'absolute';
cursor.style.zIndex = '9999';
cursor.style.width = '10px';
cursor.style.height = '10px';
cursor.style.borderRadius = '50%';
cursor.style.backgroundColor = 'red';
cursor.style.pointerEvents = 'none';
document.body.appendChild(cursor);

document.addEventListener('mousemove', function(e) {
  cursor.style.left = e.pageX - 5 + 'px';
  cursor.style.top = e.pageY - 5 + 'px';
});
'''


def random_mouse_movements(driver):
    print("Передвигаю курсор на рандомные точки...")
    for _ in range(30):
        try:
            x = random.randint(1 * _, 10 * _)
            y = random.randint(2 * _, 11 * _)
            ActionChains(driver) \
                .move_by_offset(x, y) \
                .perform()
        except Exception:
            continue


def get_random_account(old_acc=None):
    accounts_obj = []
    for obj in Account.select().iterator():
        accounts_obj.append(obj)
    if accounts_obj is None:
        return None
    random_account = random.choice(accounts_obj)
    if old_acc is not None:
        while random_account == old_acc:
            random_account = random.choice(accounts_obj)
    return random_account


def filter_answer(text: str) -> bool:
    """ Функция-фильтр для фильтрации ответов продавцов. """
    text_lower = text.lower()
    bad_words_re = r"(\s+|^)[пПnрРp]?[3ЗзВBвПnпрРpPАaAаОoO0о]?[сСcCиИuUОoO0оАaAаыЫуУyтТT]?[Ппn][иИuUeEеЕ][зЗ3][ДдDd]" \
                   r"\w*[\?\,\.\;\-]*|(\s+|^)[рРpPпПn]?[рРpPоОoO0аАaAзЗ3]?[оОoO0иИuUаАaAcCсСзЗ3тТTуУy]?[XxХх][уУy]" \
                   r"[йЙеЕeEeяЯ9юЮ]\w*[\?\,\.\;\-]*|(\s+|^)[бпПnБ6][лЛ][яЯ9]([дтДТDT]\w*)?[\?\,\.\;\-]*|(\s+|^)((" \
                   r"[зЗоОoO03]?[аАaAтТT]?[ъЪ]?)|(\w+[оОOo0еЕeE]))?[еЕeEиИuUёЁ][бБ6пП]([аАaAиИuUуУy]\w*)?[\?\,\.\;\-]*"
    if re.findall(bad_words_re, text_lower):
        return False

    for word in DENIAL_WORDS:
        if word in text_lower:
            return False
    return True


def login_to_drom(browser, random_account):
    """ Функция для логина на сайте """
    browser.get("https://my.drom.ru/sign")
    random_mouse_movements(browser)
    try:
        text_input_login = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="sign"]'))
        )
        text_input_login.send_keys(random_account.login)
        text_input_password = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="password"]'))
        )
        text_input_password.send_keys(random_account.password)

        button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="signbutton"]'))
        )
        button.click()
        try:
            try:
                result_code = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="signForm"]/form/div[2]/button'))
                )
            except Exception:
                next_code = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="signForm"]/a[2]'))
                )
                next_code.click()
                result_code = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="signForm"]/form/div[2]/button'))
                )
            result_code.click()
            phone = WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="signForm"]/div/div/div[2]'))
            )
            code = int(input(f"Введите код, пришедший на номер {phone}"))
            text_input_code = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="code"]'))
            )
            text_input_code.send_keys(code)
            button_code = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="signForm"]/form/button'))
            )
            button_code.click()


        except Exception:
            pass
    except Exception:
        print(f"Внимание! Неверные логин и пароль: {random_account.login} - {random_account.password}")
    else:
        print(f"Авторизация прошла успешно: {random_account.login} - {random_account.password}")


def send_message_to_seller(path_to_announcement, id_user, browser, account_name):
    """ Функция для отправки сообщения по объявлению """

    browser.get(path_to_announcement)

    try:
        proxy = get_proxy()
        session = get_session(proxy)
        html = session.get(path_to_announcement)
        html_code = html.text
        tree = etree.HTML(html_code)
        elem = tree.xpath("/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div/div/div[2]")[0]
        photos = list()
        for a in elem:
            if a.tag == "a":
                photos.append(a.get("href"))
    except Exception:
        print("Не удалось просмотреть фотографии!")
    print('Начинаю просмотр фотографий...')
    try:
        for photo in photos:
            try:
                browser.get(photo)
            except Exception:
                print(f"Не удалось открыть фото {photo}")
            sleep(random.choice([0.3, 0.5, 1, 2, 1.5]))

    except Exception:
        print("Что-то пошло не так с фотками!")
    else:
        print("Фотки успешно просмотрены")
    browser.get(path_to_announcement)

    try:
        price = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]'))
        ).text
    except Exception:
        price = None
    price_norm = int(''.join(price[:-2].split())) if price is not None else None
    try:
        send_button = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH,
                                            '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[6]/div/button'
                                            ))
        )
    except Exception:
        try:
            send_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[4]/div/button'
                                                ))
            )
        except Exception:
            try:
                send_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[5]/div/button"
                                                    ))
                )
            except Exception:
                print("Внимание! У данного объявления нет кнопки Отправить сообщение!")
                return
    send_button.click()
    template_dict = get_template(TEMPLATE_STRING)
    random_text = get_random_message(template_dict)
    new_price = price_rounding(price_norm, int(template_dict["percent"]))
    random_text = random_text.format(price=new_price).split()
    try:
        # Здесь получение поля
        text_input_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '/html/body/div[5]/div[2]/div/div[3]/textarea'))
        )
        for word in random_text:
            text_input_message.send_keys(f"{word} ")
            sleep(random.choice([0.3, 0.5, 1, 2, 1.5]))
        send_text_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '/html/body/div[5]/div[2]/div/div[3]/button'))
        )
        send_text_button.click()
        print(f"Сообщение отправлено: {' '.join(random_text)}")
    except Exception:
        print(f"Внимание! Превышен лимит отправленных сообщений у этого аккаунта: {account_name.login}")
        random_account = get_random_account(old_acc=account_name)
        login_to_drom(browser, random_account)
        random_mouse_movements(browser)
        send_message_to_seller(path, id_user, browser, random_account)
    # browser.close()
    # Отправка сообщения селлеру


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
        try:
            browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            browser.execute_cdp_cmd('Network.setUserAgentOverride',
                                    {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
            browser.execute_script(cursor_script)
        except Exception:
            print("Не удалось ввести скрипты для обхода капчи!")
        login_to_drom(browser, random_account)
        browser.get("https://my.drom.ru/personal/messaging-modal")
        random_mouse_movements(browser)
        messages_list = list()
        for index in range(1, 10000):
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
                    result_text = f"\nПродавец {seller_login} ответил.\n" \
                                  f"Ссылка до страницы продавца - {seller_path}\n" \
                                  f"Имя объявления: {announcement_name}\n" \
                                  f"Ссылка на объявление: {path_to_announcement}\n" \
                                  f"Цена: {price}\n" \
                                  f"Логи переписки:\n{messages}"
                    is_good = filter_answer(result_text)
                    if is_good:
                        messages_list.append(result_text)
                    else:
                        print("Внимание! Данное сообщение не прошло по фильтрам!\n"
                              f"{result_text}")

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
        for message in messages_list:
            try:
                Answer.create(text=message)
            except Exception:
                cur_answer = Answer.get(text=message)
                cur_answer.active = False
                cur_answer.save()
        answers = [answer.text for answer in Answer.select().where(Answer.active == True)]

        browser.close()
        return answers

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
    try:
        elem = tree.xpath("/html/body/div[3]/div[5]/div[1]/div[1]/div[10]/div/div[1]")[0]
    except IndexError:
        for _ in range(100):
            try:
                elem = tree.xpath("/html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[1]")[0]
            except Exception:
                print("Не удалось спарсить страницу, пробую снова!")
                sleep(random.choice([0.3, 0.5, 1, 2, 1.5]))
            else:
                print("Страница успешно загружена!")
                break
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
    interval: str = interval_obj.interval if interval_obj is not None else None
    time = MailingTime.get_or_none(id=1)
    if time is not None:
        start_time, end_time = time.start_time, time.end_time
    else:
        start_time, end_time = None, None

    cur_time = datetime.datetime.now().time()
    if interval is None:
        minutes = [1]
    else:
        start_i, stop_i = interval.split("-")
        start_i, stop_i = int(start_i.strip()), int(stop_i.strip())
        minutes = [min_i for min_i in range(start_i, stop_i + 1)]

    while True:
        if start_time is not None and end_time is not None:
            if cur_time < start_time or cur_time > end_time:
                print("Рассылка временно приостановлена, не вкладывается в тайминг.")
                sleep(60 * 60)
                continue

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
                                {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                              '(KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        browser.execute_script(cursor_script)
        login_to_drom(browser, random_account)
        random_mouse_movements(browser)

        for path in paths:
            # subprocess.Popen(f"{PATH_TO_PYTHON} handlers/custom_heandlers/work/send_message.py {path} {id_user}",
            #                  close_fds=True)
            try:
                send_message_to_seller(path, id_user, browser, random_account)
            except Exception:
                print(f"Произошла какая-то ошибка, возможно связана с капчой")
            random_interval = random.choice(minutes)
            print(f"Сообщение отправлено, сплю {random_interval} минут")
            sleep(random_interval * 60)
        break


if __name__ == '__main__':
    path, id_user = sys.argv[1], sys.argv[2]
    print("Запущен асинхронный процесс! Переданы следующие параметры:\n"
          f"Path: {path}\n"
          f"ID_USER: {id_user}\n")
    send_messages_drom(path, id_user)
