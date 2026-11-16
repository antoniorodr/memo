import os

from memo.config import CACHE_FILE
from memo.services.notes_services.cache.notes_cache_services import NotesCacheServices


def test_load_cache():
    if not os.path.exists(CACHE_FILE):
        assert NotesCacheServices.load_cache() is None
    else:
        assert NotesCacheServices.load_cache() is not None


def test_clear_cache():
    NotesCacheServices.clear_cache()
    assert not os.path.exists(CACHE_FILE)
