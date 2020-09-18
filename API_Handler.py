import requests
import base64
import os
import json

from dotenv import load_dotenv

load_dotenv()

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

login = os.getenv('USER_LOGIN')
login_bytes = login.encode('ascii')
base64_bytes = base64.b64encode(login_bytes)
base64_login = base64_bytes.decode('ascii')

level_zero_params = {
    "Authorization" : 'Basic ' + base64_login,
    "Content-Type" : 'application/json',
    "Ubi-AppId" : "86263886-327a-4328-ac69-527f0d20a237",
    "Ubi-RequestedPlatformType" : "uplay"
}

level_zero = requests.post("https://public-ubiservices.ubi.com/v3/profiles/sessions",
                            headers=level_zero_params).json()

ticket = level_zero["ticket"]

level_one_params = {
    "Authorization" : "ubi_v1 t=" + ticket
}

level_one = requests.post("https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices",
                            headers=level_one_params).json()

access_token = level_one["accessToken"]
refresh_token = level_one["refreshToken"]

level_two_params = {
    "Authorization" : "nadeo_v1 t=" + access_token
}

level_two = requests.post("https://prod.trackmania.core.nadeo.online/v2/authentication/token/nadeoservices",
                            data={'audience':'NadeoLiveServices'},
                            headers=level_two_params).json()

jprint(level_two)