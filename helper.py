import json
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def get_brand_username(filename = "brand2username.csv"):
    df = pd.read_csv("brand2username.csv")
    brands = list(df['Brand'].values)
    usernames = list(df['TikTok Username'].values)
    return (df, brands, usernames)

def mongo_login(uri):
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    return client