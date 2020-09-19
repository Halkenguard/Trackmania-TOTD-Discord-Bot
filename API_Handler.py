import requests
import base64
import os
import json

from dotenv import load_dotenv
load_dotenv()

# JPrint is only here for logging and debugging, can be removed later.
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

class TMConnector:
    def __init__(self, login):
        self.nadeo_connect(login)

    access_token_ubi = ""
    refresh_token_ubi = ""
    access_token_nadeo = ""
    refresh_token_nadeo = ""

    def nadeo_connect(self, login):
        default_headers = {
            "Content-Type": 'application/json',
            "Ubi-AppId": "86263886-327a-4328-ac69-527f0d20a237",
            "Ubi-RequestedPlatformType": "uplay"
        }

        login_bytes = login.encode('ascii')
        base64_bytes = base64.b64encode(login_bytes)
        base64_login = base64_bytes.decode('ascii')

        level_zero_params = {
            **default_headers,
            "Authorization": 'Basic ' + base64_login
        }

        level_zero = requests.post(
            "https://public-ubiservices.ubi.com/v3/profiles/sessions",
            headers=level_zero_params
        ).json()

        level_one_params = {
            **default_headers,
            "Authorization": "ubi_v1 t=" + level_zero["ticket"]
        }

        level_one = requests.post(
            "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices",
            headers=level_one_params
        ).json()

        self.access_token_ubi = level_one["accessToken"]
        self.refresh_token_ubi = level_one["refreshToken"]

        # using the default headers here seems to result in a malformed JSON in the API response?
        level_two_params = {
            "Authorization": "nadeo_v1 t=" + self.access_token_ubi
        }

        level_two = requests.post(
            "https://prod.trackmania.core.nadeo.online/v2/authentication/token/nadeoservices",
            data={'audience': 'NadeoLiveServices'},
            headers=level_two_params
        ).json()

        self.access_token_nadeo = level_two["accessToken"]
        self.refresh_token_nadeo = level_two["refreshToken"]


    def totd(self):
        # get all TOTDs
        return requests.get(
            "https://live-services.trackmania.nadeo.live/api/token/campaign/month",
            headers={"Authorization": "nadeo_v1 t=" + self.access_token_nadeo}
        ).json()


    def map_info(self, map_uid):
        # get specific map data
        return requests.get(
            "https://prod.trackmania.core.nadeo.online/maps/?mapUidList=" +
            map_uid,
            headers={"Authorization": "nadeo_v1 t=" + self.access_token_ubi}
        ).json()

# the code below should be moved to the bot once it's ready to start sending API requests

nadeo = TMConnector(os.getenv('USER_LOGIN'))

totd_list = nadeo.totd()

# get the current TOTD from the list
current_track_meta = {}
for track in totd_list["monthList"][0]["days"]:
    # if start's in the past and end's in the future, we got the current one
    if track["relativeStart"] < 0 and track["relativeEnd"] > 0:
        current_track_meta = track
        break

current_track = nadeo.map_info(current_track_meta["mapUid"])

jprint(current_track)
