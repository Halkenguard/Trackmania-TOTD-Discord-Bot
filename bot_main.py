import os
import re
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
        resolved_name = nadeo.get_user_name(map["author"])
        if resolved_name != map["author"]:
            # only set authorName if it's not the same value as the accountId (so it'll try to use the TMX name instead)
            enriched_map["authorName"] = resolved_name
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
    current_totd = enrich_map_with_username(current_totd)
    # add TMX info
    current_totd = enrich_map_with_tmx(current_totd)
    return current_totd

def format_message(totd_data):
    def format_time(raw_time):
        millisecs = raw_time[-3:]
        secs = raw_time[-5:-3]
        mins = "0"
        if len(raw_time) == 6:
            mins = raw_time[0]
        return mins + ":" + secs + "." + millisecs
    
    def remove_name_formatting(text):
        # this should take care of all the possible options, see https://doc.maniaplanet.com/client/text-formatting for reference
        text = text.replace("$w", "")
        text = text.replace("$n", "")
        text = text.replace("$o", "")
        text = text.replace("$i", "")
        text = text.replace("$t", "")
        text = text.replace("$s", "")
        text = text.replace("$g", "")
        text = text.replace("$z", "")
        text = text.replace("$$", "$")
        text = re.sub(r"\$[0-9a-fA-F]{3}", "", text)
        return text

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

    # get track name
    track_name = totd_data["name"]
    if 'tmxName' in totd_data:
        track_name = totd_data["tmxName"]
    else:
        track_name = remove_name_formatting(totd_data["name"])

    track_name = remove_name_formatting(totd_data["name"])

    # get track author
    track_author = totd_data["author"]
    if 'authorName' in totd_data:
        track_author = totd_data["authorName"]
    elif 'tmxAuthor' in totd_data:
        track_author = totd_data["tmxAuthor"]

    track = "Today's track is **" + track_name + "** by **" + track_author + "**.\n"

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
