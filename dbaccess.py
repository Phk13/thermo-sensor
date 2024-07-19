from pymongo import MongoClient
import json
from config import Config


def get_mongo_url(db):
    if db['user'] and db['pass']:
        return f"mongodb://{db['user']}:{db['pass']}@{db['host']}:{db['port']}/?authSource={db['name']}"
    else:
        return f"mongodb://{db['host']}:{db['port']}/"


def insert_read(data):
    try:
        with MongoClient(get_mongo_url(Config.DB)) as client:
            db = client[Config.DB['name']]
            result = db[Config.DB['collection']].insert_one(data)
    except Exception as e:
        print("Exception writing to mongo:", e)
        with open(Config.JSON_FILE, 'a') as f:
            json.dump(data, f, indent=4)
            f.write('\n')
