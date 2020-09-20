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


    def get_totds(self):
        # get all TOTDs
        return requests.get(
            "https://live-services.trackmania.nadeo.live/api/token/campaign/month",
            headers={"Authorization": "nadeo_v1 t=" + self.access_token_nadeo}
        ).json()


    def get_map_info(self, map_uid):
        # get in-game map data
        return requests.get(
            "https://prod.trackmania.core.nadeo.online/maps/?mapUidList=" +
            map_uid,
            headers={"Authorization": "nadeo_v1 t=" + self.access_token_ubi}
        ).json()[0]

class TMXConnector:
    def get_map_info(self, map_uid):
        # try to find the map on TMX using its Uid
        tmx_info = requests.get(
            "https://trackmania.exchange/api/tracks/get_track_info/multi/" + map_uid
        ).json()

        if len(tmx_info) == 1:
            return tmx_info[0]
        else:
            # map can't be found on TMX
            return None

# the code below should be moved to the bot once it's ready to start sending API requests

def enrich_map_with_tmx(map):
    enriched_map = map
    tmx_info = tmx.get_map_info(map["mapUid"])
    if tmx_info:
        enriched_map["tmxName"] = tmx_info["Name"]
        enriched_map["tmxStyle"] = tmx_info["StyleName"]
        enriched_map["tmxAuthor"] = tmx_info["Username"]
        enriched_map["tmxTrackId"] = tmx_info["TrackID"]
    return enriched_map

nadeo = TMConnector(os.getenv('USER_LOGIN'))
tmx = TMXConnector()

totd_list = nadeo.get_totds()

# get the current TOTD from the list
current_totd_meta = {}
for track in totd_list["monthList"][0]["days"]:
    # if start is in the past and end is in the future, it's the current one
    if track["relativeStart"] < 0 and track["relativeEnd"] > 0:
        current_totd_meta = track
        break

current_totd = enrich_map_with_tmx(
    nadeo.get_map_info(current_totd_meta["mapUid"])
)

jprint(current_totd)
