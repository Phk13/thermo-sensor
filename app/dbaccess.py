from pymongo import MongoClient
import json
from app import config


def get_mongo_url(db):
    if db['user']:
        return f"mongodb://{db['user']}:{db['pass']}@{db['host']}:{db['port']}/?authSource={db['name']}"
    else:
        return f"mongodb://{db['host']}:{db['port']}/"


def insert_read(data):
    try:
        with MongoClient(get_mongo_url(config['DB'])) as client:
            db = client[config['DB']['name']]
            result = db[config['DB']['collection']].insert_one(data)   # FIXIT
    except:
        with open(config['JSON_FILE'], 'a') as f:
            json.dump(data, f, indent=4)
            f.write('\n')
