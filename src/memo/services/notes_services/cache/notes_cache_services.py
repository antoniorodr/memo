import json
import os
import time

from memo.config import CACHE_DIR, CACHE_FILE, DEFAULT_TTL


class NotesCacheServices:
    """Service for Notes operations"""

    @staticmethod
    def save_cache(note_map, notes_list):
        os.makedirs(CACHE_DIR, exist_ok=True)
        serializable_map = {str(k): list(v) for k, v in note_map.items()}
        data = {
            "timestamp": time.time(),
            "note_map": serializable_map,
            "notes_list": notes_list,
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    @staticmethod
    def load_cache(ttl=DEFAULT_TTL):
        if not os.path.exists(CACHE_FILE):
            return None
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, KeyError):
            return None
        if time.time() - data["timestamp"] > ttl:
            return None
        note_map = {int(k): tuple(v) for k, v in data["note_map"].items()}
        return note_map, data["notes_list"]

    @staticmethod
    def clear_cache():
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
