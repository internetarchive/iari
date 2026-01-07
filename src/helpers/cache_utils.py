import hashlib
import os
from typing import Any

import config
import json
from os.path import exists

from datetime import datetime
from src.models.exceptions import UnknownValueError

from enum import Enum


class CacheType(Enum):
    probes = "probes"
    status = "status"
    signals = "signals"


def get_cache_hash(cache_title: str, cache_type: CacheType):
    """
    returns "hash" value based on cacheType
    if cacheType is probes or status, the hash is md5 encosion of string (assumed a url)
    if cacheType is signals, hash is just the string supplied, assumed to be a domain name
    """

    # return direct domain name if cacheType is signals
    if cache_type == CacheType.signals:
        return cache_title
    # else return md5 hash of string
    # - assume cache_title is a URL
    # - 16 characters should give us enough uniqueness
    return hashlib.md5(cache_title.encode()).hexdigest()[:16]


def get_cache_file_path(cache_title: str, cache_type: CacheType, variety: str = ""):
    """
    cache path is determined by cache_type
    variety is the prefix for the final file name
    """
    cache_path = f"{config.iari_cache_dir}{cache_type.value}"

    # error if type not found as a subdir
    if not os.path.isdir(cache_path):
        raise UnknownValueError(f"Unsupported cache type \"{cache_type.value}\" (json path \"{cache_path}\" does not exist).")

    cache_hash = get_cache_hash(cache_title.upper(), cache_type=cache_type)

    cache_name = f"{variety.upper() + '-' if variety else ''}{cache_hash}.json"

    # calc filename
    return f"{cache_path}/{cache_name}"


def get_cache(cache_title: str, cache_type: CacheType, variety: str = ""):
    """
    return JSON of cached value found or None if not found

    cache_type determines the json subdirectory cache value is located
    variety is the prefix
    url gets transformed into an md5 hash
        (or something else in the future if deemed necessary)

    """

    cache_file_path = get_cache_file_path(cache_title, cache_type, variety)

    # return None if file does not yet exist
    if not exists(cache_file_path):
        return None

    # return payload; assume saved in json format
    with open(file=cache_file_path) as file:
        payload = json.load(file)
        return payload


def set_cache(cache_title: str, cache_type: CacheType, variety: str = "", payload: Any = None):
    """
    sets payload as cached value

    TODO: check error behavior when json cache path does not exist
    """

    cache_file_path = get_cache_file_path(cache_title, cache_type, variety)

    from src import app
    app.logger.debug(f"cache id for url {cache_title} is {cache_file_path}")

    # overwrite if already exists
    if exists(cache_file_path):
        with open(file=cache_file_path, mode="w") as file:
            # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
            json.dump(payload, file, ensure_ascii=False, indent=4)

    # else create cache (mode "x" = create and write)
    else:
        with open(file=cache_file_path, mode="x") as file:
            # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
            json.dump(payload, file, ensure_ascii=False, indent=4)


def is_cached(cache_title: str, cache_type: CacheType, variety: str = ""):
    """
    """
    cache_file_path = get_cache_file_path(cache_title, cache_type, variety)
    return exists(cache_file_path)


if __name__ == "__main__":
    print("get_cache - no CLI yet...")
