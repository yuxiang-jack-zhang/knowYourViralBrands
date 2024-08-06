import pandas as pd
import json
from datetime import datetime

def clean_user_data(dicts: list, usernames: list):
    """
    Helper function to clean and unpack nested scraped tiktok data
    INPUT: [ {...}, {}, ... , {} ] list of nested dicts, each dict is entry in database
    OUTPUT: {
        "brand1_username": {
            "timestamp": [],
            "followerCount": [],
            etc...}
        "brand2_usernames": {etc...},
        etc...
    }
    """
    # Initialize output
    output = {username: {"timestamp": [],
              "followerCount": [],
              "heartCount": [],
              "videoCount": []} for username in usernames}

    for entry in dicts:
        # read data for each entry in input data from database
        brandusername = entry['userInfo']['user']['uniqueId']
        # timestamp = datetime.fromtimestamp(entry['extra']['now']/1000).strftime('%Y-%m-%d') # %H:%M:%S')
        timestamp = entry['extra']['now']
        followerCount = entry['userInfo']['stats']['followerCount']
        heartCount = entry['userInfo']['stats']['heartCount']
        videoCount = entry['userInfo']['stats']['videoCount']

        # put data in the right place in output dict
        output[brandusername]['timestamp'].append(timestamp)
        output[brandusername]['followerCount'].append(followerCount)
        output[brandusername]['heartCount'].append(heartCount)
        output[brandusername]['videoCount'].append(videoCount)
    return output



def clean_video_data(data):
    nested_values = ["author", "authorStats", "stats", "statsV2"]

    # "contents" contains a copy of "desc" and "textExtra", so we skip it
    skip_values = ["challenges", "music", "video", "contents", "duetInfo", "item_control"]

    flattened_data = {}
    # Loop thru each video
    for idx, value in enumerate(data):
        flattened_data[idx] = {}
        # Loop thru each property in each video
        for prop_idx, prop_value in value.items():
            # Check if skip
            if prop_idx in skip_values:
                pass
            # Hardcode how to parse hashtag names, which is a list of dicts stored under "textExtra"
            elif prop_idx == "textExtra":
                hashtags = ""
                for hashtag in prop_value:
                    hashtags += hashtag["hashtagName"] + ","
                flattened_data[idx]['hashtags'] = hashtags[:-1]
            # Hardcode how to parse text on video
            elif prop_idx == "stickersOnItem":
                stickers = ""
                for sticker in prop_value:
                    for text in sticker['stickerText']:
                        stickers += text + ","
                flattened_data[idx]['textOnVideo'] = stickers[:-1]
            # Check if nested
            elif prop_idx in nested_values:
                # Loop thru each nested property
                for nested_idx, nested_value in prop_value.items():
                    flattened_data[idx][prop_idx+'_'+nested_idx] = nested_value
            # If it's not nested, add it back to the flattened dictionary 
            else: 
                flattened_data[idx][prop_idx] = prop_value
    return flattened_data