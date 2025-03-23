import sqlite3
import json
from typing import List, Dict, Any

class LocalStorage:
    def __init__(self, db_path: str = "readings.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sync_status TEXT DEFAULT 'pending',
                    sync_timestamp DATETIME
                )
            """)
            conn.commit()

    def store_reading(self, data: Dict[str, Any]) -> int:
        """Store a new reading in the local database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO readings (data) VALUES (?)",
                (json.dumps(data),)
            )
            conn.commit()
            return cursor.lastrowid

    def get_pending_readings(self, limit: int = 100) -> List[tuple]:
        """Retrieve readings that haven't been synced to MongoDB yet."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, data FROM readings 
                WHERE sync_status = 'pending'
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                (limit,)
            )
            return cursor.fetchall()

    def mark_synced(self, reading_ids: List[int]):
        """Mark readings as successfully synced to MongoDB."""
        if not reading_ids:
            return
            
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ','.join('?' * len(reading_ids))
            conn.execute(
                f"""
                UPDATE readings 
                SET sync_status = 'synced',
                    sync_timestamp = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders})
                """,
                reading_ids
            )
            conn.commit()

    def cleanup_old_synced(self, days: int = 7):
        """Remove synced readings older than specified days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                DELETE FROM readings
                WHERE sync_status = 'synced'
                AND sync_timestamp < datetime('now', ?)
                """,
                (f'-{days} days',)
            )
            conn.commit()
