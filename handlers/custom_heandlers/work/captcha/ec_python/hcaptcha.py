import json
from endcaptcha import HttpClient
import sys


if __name__ == '__main__':
    try:
        ec_username = sys.argv[1]
        ec_password = sys.argv[2]

        client = HttpClient(ec_username, ec_password)
        # client.is_verbose = True

        # Get Balance - (get_balance)
        captcha = client.get_balance()
        print(captcha)

        ##########################################
        #      Recaptcha V3 Upload Sample
        ##########################################
        token_dict = {
            "proxy": "",  "proxytype": "",
            "sitekey": "a5f74b19-9e45-40e0-b45d-47ff91b7a6c2",
            "pageurl": "https://accounts.hcaptcha.com/demo"
        }
        hcaptcha_params = json.dumps(token_dict)
        # Decode Token CAPTCHA - (decode)
        captcha = client.decode(type=7, hcaptcha_params=hcaptcha_params)
        print(captcha)
        ##########################################

        # Get poll CAPTCHA - (get_captcha)
        captcha = client.get_captcha('247021718')
        print(captcha)

        # # Report CAPTCHA by captcha_id
        # captcha = client.report('123456789')
        # print(captcha)
    except Exception as e:
        print(e)
