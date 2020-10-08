import os
from datetime import datetime

import discord
from dotenv import load_dotenv

import API_Handler

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

def get_totd_data():
    nadeo = API_Handler.TMConnector(os.getenv('USER_LOGIN'))
    tmx = API_Handler.TMXConnector()

    def enrich_map_with_username(map):
        enriched_map = map
        enriched_map["authorName"] = nadeo.get_user_info(map["author"])
        return enriched_map

    def enrich_map_with_tmx(map):
        enriched_map = map
        tmx_info = tmx.get_map_info(map["mapUid"])
        if tmx_info != None:
            enriched_map["tmxName"] = tmx_info["Name"]
            enriched_map["tmxStyle"] = tmx_info["StyleName"]
            enriched_map["tmxAuthor"] = tmx_info["Username"]
            enriched_map["tmxTrackId"] = tmx_info["TrackID"]
        return enriched_map
    
    totd_list = nadeo.get_totds()

    # get the current TOTD from the list
    current_totd_meta = {}
    for track in totd_list["monthList"][0]["days"]:
        # if start is in the past and end is in the future, it's the current one
        if track["relativeStart"] < 0 and track["relativeEnd"] > 0:
            current_totd_meta = track
            break

    # get initial map
    current_totd = nadeo.get_map_info(current_totd_meta["mapUid"])
    # add author's username
    #current_totd = enrich_map_with_username(current_totd)
    # add TMX info
    current_totd = enrich_map_with_tmx(current_totd)
    return current_totd

def format_message(totd_data):
    # assemble title
    today = datetime.now().strftime("%B %d")
    if today[len(today) - 1] == "1":
        today += "st"
    elif today[len(today) - 1] == "2":
        today += "nd"
    elif today[len(today) - 1] == "3":
        today += "rd"
    else:
        today += "th"
    title = "**The " + today + " Track of the Day is now live!**\n"

    # assemble track info
    track_name = totd_data["name"]
    if hasattr(totd_data, 'tmxName'):
        track_name = totd_data["tmxName"]
    # TODO: if there's no tmxName, we need to parse out the formatting codes (colors etc.)
    # TODO: resolve the author's name
    track_author = totd_data["author"]
    track = "Today's track is **" + track_name + "** by **" + track_author + "**.\n"

    def format_time(raw_time):
        millisecs = raw_time[-3:]
        secs = raw_time[-5:-3]
        mins = "0"
        if len(raw_time) == 6:
            mins = raw_time[0]
        return mins + ":" + secs + "." + millisecs

    # assemble medal info
    bronze = "<:MedalBronze:763718615764566016> Bronze: ||" + \
        format_time(str(totd_data["bronzeScore"])) + "||\n"
    silver = "<:MedalSilver:763718615689330699> Silver: ||" + \
        format_time(str(totd_data["silverScore"])) + "||\n"
    gold = "<:MedalGold:763718328685559811> Gold: ||" + \
        format_time(str(totd_data["goldScore"])) + "||\n"
    author = "<:MedalAuthor:763718159714222100> Author: ||" + \
        format_time(str(totd_data["authorScore"])) + "||\n"
    medals = "Medal times:\n" + bronze + silver + gold + author + "\n"
    scoreNote = "React to this message below to rate the TOTD!"
    
    return title + track + medals + scoreNote

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(client.guilds[1].channels[2].name)
    try:
        totd_data = get_totd_data()
        # TODO: figure out how this should determine in which guilds/channels it should post (maybe the first channel in every server with 'totd' in their name)
        message = await client.guilds[1].channels[2].send(format_message(totd_data))
        
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        for emoji in emojis:
            await message.add_reaction(emoji)
    except Exception as e:
        print(e)
    
    # TODO: gracefully close the process when it's done
    # for some reason, this causes an "Event loop is closed" exception though
    #await client.close()

client.run(TOKEN)

# test track data
test = {
    'author': '0f400a09-023c-4787-87ed-72261460f337',
    'authorScore': 43061,
    'bronzeScore': 105000,
    'collectionName': 'Stadium',
    'environment': 'Stadium',
    'filename': 'Avalanche!.Map.Gbx',
    'goldScore': 46000,
    'isPlayable': True,
    'mapId': '356edc8c-0999-4789-adb6-d3bdf938bac0',
    'mapUid': 'ecpfGu8TywF7HDyaMXHT5ApXv8g',
    'name': 'Avalanche!',
    'silverScore': 52000,
    'submitter': '0f400a09-023c-4787-87ed-72261460f337',
    'timestamp': '2020-09-29T21:24:42+00:00',
    'fileUrl': 'https://prod.trackmania.core.nadeo.online/storageObjects/89671a11-cdbd-4be3-b890-dedef09a9bfc',
    'thumbnailUrl': 'https://prod.trackmania.core.nadeo.online/storageObjects/3c19e9dc-1726-4176-beb2-4cf22e2cbaee.jpg',
    'tmxName': 'Avalanche!',
    'tmxStyle': 'Competitive',
    'tmxAuthor': 'Paulmar35',
    'tmxTrackId': 17755
}
