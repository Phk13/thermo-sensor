from pymongo import MongoClient
import json
from config import Config
from local_storage import LocalStorage
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize local storage
local_db = LocalStorage()

def get_mongo_url(db):
    if db['user'] and db['pass']:
        return f"mongodb://{db['user']}:{db['pass']}@{db['host']}:{db['port']}/?authSource={db['name']}"
    else:
        return f"mongodb://{db['host']}:{db['port']}/"

def sync_to_mongo():
    """Background process to sync pending readings to MongoDB."""
    while True:
        try:
            # Get pending readings
            pending = local_db.get_pending_readings(limit=100)
            if not pending:
                time.sleep(60)  # Wait a minute before next sync attempt
                continue

            successful_ids = []
            with MongoClient(get_mongo_url(Config.DB)) as client:
                db = client[Config.DB['name']]
                collection = db[Config.DB['collection']]
                
                for reading_id, data_str in pending:
                    try:
                        data = json.loads(data_str)
                        collection.insert_one(data)
                        successful_ids.append(reading_id)
                    except Exception as e:
                        logger.error(f"Failed to sync reading {reading_id}: {e}")

            if successful_ids:
                local_db.mark_synced(successful_ids)
                logger.info(f"Successfully synced {len(successful_ids)} readings")

            # Cleanup old synced records
            local_db.cleanup_old_synced(days=7)

        except Exception as e:
            logger.error(f"Sync process error: {e}")
            time.sleep(60)  # Wait before retry on error

def insert_read(data):
    """Store reading in local storage and attempt immediate MongoDB sync."""
    try:
        # Always store in local storage first
        reading_id = local_db.store_reading(data)
        logger.info(f"Stored reading {reading_id} locally")

        # Attempt immediate MongoDB sync
        with MongoClient(get_mongo_url(Config.DB)) as client:
            db = client[Config.DB['name']]
            db[Config.DB['collection']].insert_one(data)
            local_db.mark_synced([reading_id])
            logger.info(f"Successfully synced reading {reading_id} to MongoDB")
    except Exception as e:
        logger.error(f"MongoDB sync error: {e}")
        logger.info("Reading stored locally, will be synced later")

# Start background sync process
sync_thread = threading.Thread(target=sync_to_mongo, daemon=True)
sync_thread.start()
