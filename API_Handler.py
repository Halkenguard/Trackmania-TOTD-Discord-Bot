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

default_headers = {
    "Content-Type": 'application/json',
    "Ubi-AppId": "86263886-327a-4328-ac69-527f0d20a237",
    "Ubi-RequestedPlatformType": "uplay"
}

level_zero_params = {
    **default_headers,
    "Authorization": 'Basic ' + base64_login
}

level_zero = requests.post(
    "https://public-ubiservices.ubi.com/v3/profiles/sessions",
    headers=level_zero_params
).json()

ticket = level_zero["ticket"]

level_one_params = {
    **default_headers,
    "Authorization": "ubi_v1 t=" + ticket
}

level_one = requests.post(
    "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices",
    headers=level_one_params
).json()

access_token_ubi = level_one["accessToken"]
refresh_token_ubi = level_one["refreshToken"]

# using the default headers here seems to result in a malformed JSON in the API response?
level_two_params = {
    "Authorization": "nadeo_v1 t=" + access_token_ubi
}

level_two = requests.post(
    "https://prod.trackmania.core.nadeo.online/v2/authentication/token/nadeoservices",
    data={'audience': 'NadeoLiveServices'},
    headers=level_two_params
).json()

access_token_nadeo = level_two['accessToken']
refresh_token_nadeo = level_two['refreshToken']

# get the current month of TOTDs
totd = requests.get(
    "https://live-services.trackmania.nadeo.live/api/token/campaign/month",
    headers={"Authorization": "nadeo_v1 t=" + access_token_nadeo}
).json()

# get the current TOTD from the list
current_track_meta = {}
for track in totd["monthList"][0]["days"]:
    if track["relativeStart"] < 0 and track["relativeEnd"] > 0:
        current_track_meta = track
        break

# get the current TOTD map data
current_track = requests.get(
    "https://prod.trackmania.core.nadeo.online/maps/?mapUidList=" +
    current_track_meta["mapUid"],
    headers={"Authorization": "nadeo_v1 t=" + access_token_ubi}
).json()

jprint(current_track)
