# import core flask and pymongo utilities
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import json_util

# import native utilities
from datetime import datetime
import os, json

# import custom functions
from tiktok_data_cleaning import clean_user_data
from helper import get_brand_username, mongo_login

app = Flask(__name__)
CORS(app)

# MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://jackzhang1298:youlanjiyi@sbcluster.surcdnj.mongodb.net/?retryWrites=true&w=majority&appName=SBCluster"
# Fetch data from MongoDB
client = mongo_login(MONGO_URI)
# Select the database and collection
db = client['knowYourViralBrands']
collection = db['TikTokAccount']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/data')
def get_data():
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
    datasets = []
    for username, user_data in data.items():
        # get the brand for tiktok username
        brand = df.loc[df['TikTok Username'] == username]['Brand'].values[0]

        datasets.append({
            'label': brand,
            'followerCount': [{'x': t, 'y': c} for t,c in zip(user_data['timestamp'], user_data['followerCount'])],
            'heartCount': [{'x': t, 'y': c} for t,c in zip(user_data['timestamp'], user_data['heartCount'])],
            'videoCount': [{'x': t, 'y': c} for t,c in zip(user_data['timestamp'], user_data['videoCount'])],
            'heart2videoRatio': [{'x': t, 'y': h/v} for t,h,v in zip(user_data['timestamp'], user_data['heartCount'], user_data['videoCount'])],
            'fill': False,
            'borderColor': f'rgb({hash(brand) % 256}, {(hash(brand) // 256) % 256}, {(hash(brand) // 65536) % 256})',
            'tension': 0.1
        })

        # find the min and max timestamps
        min_timestamp = float('inf')
        max_timestamp = float('-inf')
        min_timestamp = min([min_timestamp] + user_data['timestamp'])
        max_timestamp = max([max_timestamp] + user_data['timestamp'])

    return jsonify({
        'labels': brands,
        'datasets': datasets,
        'min_timestamp': min_timestamp,
        'max_timestamp': max_timestamp
    })

@app.route('/api/tiktok_trends', methods=['GET'])
def get_tiktok_trends():
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

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
