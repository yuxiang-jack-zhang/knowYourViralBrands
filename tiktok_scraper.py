# import core web-scraper dependencies
from TikTokApi import TikTokApi
import asyncio
import os, json

# import mongoDB packages
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# import custom helper functions
from helper import get_brand_username

ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com

async def get_user_data(usernames):
    """
    input: list of tiktok usernames to scrape
    output: list of dictionaries, each dict is data for each user
    """
    dicts = []
    api = TikTokApi()
    await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
    for username in list(usernames):
        user = api.user(username)

        # wrap the scrape step in custom error message to make debugging easier
        try:
            user_data = await user.info()
        except:
            raise ValueError(f"Error when scraping username '{username}', please check for typos in input username sequence.")
        
        dicts.append(user_data)

        # async for video in user.videos(count=30):
        #     print(video)
        #     print(video.as_dict)
    return dicts

def backup(new_data, fname="backup.json"):
    if not os.path.isfile(fname):
        print(f"! Backup file '{fname}' not found, creating new file to dump data.")
        with open(fname, mode='w') as f:
            f.write(json.dumps(new_data))
    else:
        print(f"Backup file found.")
        try: 
            with open(fname) as backupjson:
                old_data = json.load(backupjson)
            for new_entry in new_data:
                old_data.append(new_entry)
            with open(fname, mode='w') as f:
                f.write(json.dumps(old_data, indent=2))
        except Exception as e:
            print("Backup failed! Maybe ping developer's email here.")
            print(e)

    return 

def upload_to_mongo(data=None):
    MONGO_URI = os.environ.get('MONGO_URI')

    # Create a new client and connect to the server
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB.")
    except Exception as e:
        print(e)

    # Select the database and collection
    db = client['knowYourViralBrands']
    collection = db['TikTokAccount']

    # load data if it's not passed in
    if not data:
        with open("tiktok_data_user.json", 'r') as file:
            data = json.load(file)

    # insert data
    insertResult = collection.insert_many(data)
    print(f"Successfully inserted {len(data)} entries into database '{db.name}' collection '{collection.name}'.")


def main(outname = "tiktok_data_user.json"):
    """
    Scrapes TikTok user data for users specified in brand2username.csv
    And writes output data to json file, outname default to "tiktok_data_user.json"
    """
    # load file that maps brand name to tiktok username
    (df, brands, usernames) = get_brand_username()

    # scrape current user data
    dicts = asyncio.run(get_user_data(usernames))
    print("Finished scraping TikTok.")

    # Export scraped data (list of dictionaries) to json
    with open(outname, 'w') as f:
        json.dump(dicts, f, indent=2)
    print("Finished writing out TikTok data.")
    
    # backup scraped data locally, default to backup.json
    backup(dicts)
    print("Backup done.")
    
    # Upload scraped data to MongoDB
    upload_to_mongo(data=dicts)
    print("Finished uploading to MongoDB Atlas.")


    return 

if __name__ == "__main__":
    main()

# brandname2username = {
#     "Oats Overnight": "oatsovernight",
#     "Kodiak Cakes": "kodiakcakes",
#     "Mush": "mush",
#     "Quaker": "quaker",
#     "Magic Spoon": "magicspooncereal",
#     "Birch Benders": "birchbenders",
#     "Catalina Krunch": "catalinacrunch",
#     "Purely Elizabeth": "purely_elizabeth",
#     "ONO Overnight Oats": "eatovernightoats",
#     "Yishi Foods": "yishifoods",
#     "Mylk Labs Oatmeal": "mylklabs",
#     "Bob's Red Mill": "bobsredmill"
#     }