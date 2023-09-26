# **Drom bot**


Данный бот умеет делать рассылку сообщений в Дром.

## Used technology

* Python (3.10)
* PyTelegramBotApi (Telegram Bot framework)
* SQLite3 (database)
* requests (2.28.1)
* telebot-calendar (1.2)
* Peewee (3.16.2)


## Installation


1. Необходимо скопировать все содержимое репозитория в отдельный каталог.
2. Установить все библиотеки из requirements.txt
3. Файл .env.template переименуйте в .env. Откройте его и заполните необходимыми данными. Для этого вам надо:
    * Создать своего бота с помощью @BotFather, запросить токен
4. Установка Selenium
   * Узнаем свою версию браузера Chrome [здесь](chrome://settings/help)
   * Переходим по этой [ссылке](https://sites.google.com/chromium.org/driver/downloads) и качаем драйвер, подходящий по версии. Если вашей версии там нет, поищите вот на [этой](https://googlechromelabs.github.io/chrome-for-testing/#stable) странице.
   * Распаковываем скачанный архив в эту папку - C:/chromedriver (необходимо предварительно её создать)
   * Если вы по какой-то необходимости распаковали драйвер в другую папку, нужно в файле config_data/config.py указать путь к этому драйверу в переменной DRIVER_PATH.
5. Запустите файл **main**.py.