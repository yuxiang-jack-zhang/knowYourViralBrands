# import core flask and pymongo utilities
from flask import Flask, render_template, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# import native utilities
from datetime import datetime
import os

# import custom functions
from tiktok_data_cleaning import clean_user_data
from helper import get_brand_username

app = Flask(__name__)

# MongoDB Atlas connection string
MONGO_URI = os.environ.get('MONGO_URI')

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Fetch data from MongoDB
    client = mongo_login(MONGO_URI)
    # Select the database and collection
    db = client['knowYourViralBrands']
    collection = db['TikTokAccount']

    # load file that maps brand name to tiktok username
    (df, brands, usernames) = get_brand_username()

    # Query the data we care about using projection
    projection = {
        '_id': 0,
        'extra.now': 1,
        'extra.logID': 1,
        'userInfo.user.uniqueId': 1,
        'userInfo.user.nickname': 1,
        'userInfo.stats.followerCount': 1,
        'userInfo.stats.heartCount': 1,
        'userInfo.stats.videoCount': 1
    }
    dicts = list(collection.find({}, projection))

    # Clean up data queried from mongoDB
    data = clean_user_data(dicts, usernames)

    # Prepare datasets for Chart.js

    min_timestamp = float('inf')
    max_timestamp = float('-inf')

    # For followerCount
    datasets = []
    for username, user_data in data.items():
        # get the brand for tiktok username
        brand = df.loc[df['TikTok Username'] == username]['Brand'].values[0]

        datasets.append({
            'label': brand,
            'data': [{'x': t, 'y': c} for t,c in zip(user_data['timestamp'], user_data['followerCount'])],
            'fill': False,
            'borderColor': f'rgb({hash(brand) % 256}, {(hash(brand) // 256) % 256}, {(hash(brand) // 65536) % 256})',
            'tension': 0.1
        })

        # find the min and max timestamps
        min_timestamp = min([min_timestamp] + user_data['timestamp'])
        max_timestamp = max([max_timestamp] + user_data['timestamp'])
    min_timestamp -= 86400
    max_timestamp += 86400

    return jsonify({
        'labels': brands,
        'datasets': datasets,
        'min_timestamp': min_timestamp,
        'max_timestamp': max_timestamp
    })



if __name__ == '__main__':
    app.run(debug=True)
