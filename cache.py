import json
import os
import time
from pathlib import Path

CACHE_DIR = ".cache"
CACHE_EXPIRY = {
    "calendar": 86400,      # 24 hours
    "gmail": 3600,           # 1 hour
    "weather": 3600,         # 1 hour
    "news": 21600,           # 6 hours
    "quote": 86400,          # 24 hours
}


def _ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    Path(CACHE_DIR).mkdir(exist_ok=True)


def get_cached_data(data_type, max_age_seconds=None):
    """Get cached data if it exists and is fresh, else return None"""
    if max_age_seconds is None:
        max_age_seconds = CACHE_EXPIRY.get(data_type, 3600)

    cache_file = os.path.join(CACHE_DIR, f"{data_type}.json")

    if not os.path.exists(cache_file):
        return None

    try:
        age = time.time() - os.path.getmtime(cache_file)
        if age < max_age_seconds:
            with open(cache_file, "r") as f:
                return json.load(f)
    except (IOError, json.JSONDecodeError):
        pass

    return None


def set_cache(data_type, data):
    """Store data in cache"""
    _ensure_cache_dir()
    cache_file = os.path.join(CACHE_DIR, f"{data_type}.json")

    try:
        with open(cache_file, "w") as f:
            json.dump(data, f, default=str)  # default=str for datetime serialization
    except IOError as e:
        print(f"Warning: Failed to cache {data_type}: {e}")


def clear_cache(data_type=None):
    """Clear cache for specific data type or all"""
    _ensure_cache_dir()

    if data_type:
        cache_file = os.path.join(CACHE_DIR, f"{data_type}.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)
    else:
        import shutil
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)


def is_cache_fresh(data_type):
    """Check if cache exists and is fresh without retrieving data"""
    max_age = CACHE_EXPIRY.get(data_type, 3600)
    cache_file = os.path.join(CACHE_DIR, f"{data_type}.json")

    if not os.path.exists(cache_file):
        return False

    age = time.time() - os.path.getmtime(cache_file)
    return age < max_age
