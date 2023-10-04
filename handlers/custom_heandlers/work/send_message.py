import re
import time
from time import sleep
import sys
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from config_data.config import DRIVER_PATH, TEMPLATE_STRING, DENIAL_WORDS
from handlers.custom_heandlers.work.get_template import price_rounding, get_template, get_random_message
from database.models import Account, Answer, Proxy
import requests
import random

options = Options()
# options.add_argument("--headless")
options.add_argument("--incognito")
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)


def get_random_account():
    accounts_obj = []
    for obj in Account.select().iterator():
        accounts_obj.append(obj)
    if accounts_obj is None:
        return None
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
    time.sleep(5)
    browser.get("https://my.drom.ru/sign")
    time.sleep(5)
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


def send_message_to_seller(path_to_announcement, id_user):
    """ Функция для отправки сообщения по объявлению """
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
    login_to_drom(browser, random_account)

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
        send_button = WebDriverWait(browser, 10).until(
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
            return
    send_button.click()
    template_dict = get_template(TEMPLATE_STRING)
    random_text = get_random_message(template_dict)
    new_price = price_rounding(price_norm, int(template_dict["percent"]))
    random_text = random_text.format(price=new_price)

    # Здесь получение поля
    text_input_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH,
                                        '/html/body/div[5]/div[2]/div/div[3]/textarea'))
    )
    text_input_message.send_keys(random_text)
    send_text_button = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH,
                                        '/html/body/div[5]/div[2]/div/div[3]/button'))
    )
    send_text_button.click()
    print(f"Сообщение отправлено: {random_text}")
    browser.close()
    # Отправка сообщения селлеру


if __name__ == '__main__':
    path, id_user = sys.argv[1], sys.argv[2]
    send_message_to_seller(path, id_user)
