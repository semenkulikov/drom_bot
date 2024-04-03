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
            "googlekey": "6LdyC2cUAAAAACGuDKpXeDorzUDWXmdqeg-xy696",
            "pageurl": "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php",
            "action":  "examples/v3scores",
            "min_score": 0.3
        }
        token_params = json.dumps(token_dict)
        # Decode Token CAPTCHA - (decode)
        captcha = client.decode(type=5, token_params=token_params)
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
