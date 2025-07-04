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


def get_cache_hash(string: str):
    # 16 characters should give us enough uniqueness...
    return hashlib.md5(string.encode()).hexdigest()[:16]


def get_cache_file_path(url, cache_type: CacheType, variety):
    json_path = f"{config.subdirectory_for_json}{cache_type.value}"

    # error if type not found as a subdir
    if not os.path.isdir(json_path):
        raise UnknownValueError(f"Unsupported cache type \"{cache_type.value}\" (json path \"{json_path}\" does not exist).")

    url_hash = get_cache_hash(url.upper())

    # prefix: uppercase of variety
    prefix = variety.upper()

    # calc filename
    return f"{json_path}/{prefix}-{url_hash}.json"


def get_cache(url, cache_type: CacheType, variety):
    """
    return json format of cached value found or None if not found

    cache_type determines the json subdirectory cache value is located
    variety is the prefix
    url gets transformed into an md5 hash
        (or something else in the future if deemed necessary)

    """

    cache_file_path = get_cache_file_path(url, cache_type, variety)

    # return None if file does not yet exist
    if not exists(cache_file_path):
        return None

    # return payload; assume saved in json format
    with open(file=cache_file_path) as file:
        payload = json.load(file)
        return payload


def set_cache(url: str, cache_type: CacheType, variety: str, payload: Any):
    """
    sets payload as cached value

    TODO: check error behavior when json cache path does not exist
    """

    cache_file_path = get_cache_file_path(url, cache_type, variety)

    from src import app
    app.logger.debug(f"cache id for url {url} is {cache_file_path}")

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


def is_cached(url, cache_type: CacheType, variety):
    """
    """
    cache_file_path = get_cache_file_path(url, cache_type, variety)
    return exists(cache_file_path)


if __name__ == "__main__":
    print("get_cache - no CLI yet...")
