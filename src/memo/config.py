import os

FOLDER_SEPARATOR = "|||"
CACHE_DIR = os.path.expanduser("~/.cache/memo")
CACHE_FILE = os.path.join(CACHE_DIR, "notes_cache.json")
DEFAULT_TTL = 300  # 5 minutes
