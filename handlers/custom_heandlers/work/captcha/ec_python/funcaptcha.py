import json
from endcaptcha import HttpClient
import sys
import urllib.parse


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
            "publickey": "E8A75615-1CBA-5DFF-8032-D16BCF234E10",
            "pageurl": "https://account.battle.net/creation/flow/creation-full"
        }
        funcaptcha_params = json.dumps(token_dict)
        # Decode Token CAPTCHA - (decode)
        captcha = client.decode(type=6, funcaptcha_params=funcaptcha_params)
        print(captcha)
        print(f"Decoded solution: {urllib.parse.unquote(captcha['text'])}")
        ##########################################

        # Get poll CAPTCHA - (get_captcha)
        # captcha = client.get_captcha('660726324')
        # print(captcha)
        

        # # Report CAPTCHA by captcha_id
        # captcha = client.report('123456789')
        # print(captcha)
    except Exception as e:
        print(e)
