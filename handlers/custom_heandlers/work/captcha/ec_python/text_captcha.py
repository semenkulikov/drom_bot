import json
from endcaptcha import HttpClient
import sys


if __name__ == '__main__':
    try:
        ec_username = sys.argv[1]
        ec_password = sys.argv[2]
        image = sys.argv[3]

        client = HttpClient(ec_username, ec_password)
        # client.is_verbose = True

        # Get Balance - (get_balance)
        captcha = client.get_balance()
        print(captcha)

        ##########################################
        #      TEXT Captcha Upload Sample
        ##########################################
        # Upload text CAPTCHA image - (upload)
        captcha = client.upload(image)
        print(captcha)
        ##########################################

        # Get poll CAPTCHA - (get_captcha)
        captcha = client.get_captcha('247021718')
        print(captcha)

        # # Report CAPTCHA image
        # captcha = client.report(image)
        # print(captcha)

        # # Report CAPTCHA by captcha_id
        # captcha = client.report('123456789')
        # print(captcha)
    except Exception as e:
        print(e)
