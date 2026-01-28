import pandas as pd
import pickle
import config

from src.models.exceptions import IariFetchError
from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType


SIGNALS_CACHE_DIR = f"{config.iari_cache_dir}"
SIGNALS_CSV = config.iari_signals_csv


def load_signal_data(force_refresh=False):
    """
    Loads signal data either from a cache file or from a CSV file if the cache is not available or
    if cache refresh is forced.

    This function first checks if the cached data exists and the user doesn't explicitly request a
    refresh of the cache (`force_refresh`). If the cache is valid, data is loaded from the cache file.
    Otherwise, the data is loaded from a specified CSV file and saved into the cache for future use.

    The cache directory is created if it does not exist.

    Parameters:
        force_refresh (bool): Flag to determine whether to force a refresh by loading data from the
                              CSV file instead of the cache file. Defaults to False.

    Returns:
        pd.DataFrame: The signal data loaded either from the cache file or the CSV file.
    """

    # pull from cache if there...
    import os
    os.makedirs(SIGNALS_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(SIGNALS_CACHE_DIR, f"wiki_signals.pickle")

    from src import app
    # app.logger.debug(f"==> load_signal_data:: cache_path is {cache_path}, force_refresh = {force_refresh}")

    # ✅ Step 1: Load from cache if exists and not forcing refresh
    if not force_refresh and os.path.exists(cache_path):
        # app.logger.debug(f"==> load_signal_data:: Loading wiki_signal data from cache...")
        with open(cache_path, "rb") as f:
            return pickle.load(f)
            ### return pd.read_parquet(cache_path)

    # if not found in cache, fetch fresh and then save in cache before returning
    # ✅ Step 2: Fetch data from CSV file if not cached
    app.logger.debug(f"Fetching wiki_signal data from csv file: {SIGNALS_CSV}...")

    df_from_csv = pd.read_csv(SIGNALS_CSV, index_col=0)
    # TODO any massaging of data here...

    # ✅ Step 3: Cache dataframe to disk
    app.logger.debug(f"Saving wiki_signal dataframe to cache...")
    with open(cache_path, "wb") as f:
        pickle.dump(df_from_csv, f)
    return df_from_csv


def get_signal_data_for_domain(domain, force_refresh=False):
    """
    grabs signal data for domain from Wiki Signal data

    for now, grabbing signal data from local cache
    - eventually will come from WikiSignals API

    uses domain as key to extract data from "database"
    - get dataframe
        - get cached dataframe file from disk if there (parquet? csv?)
        - create dataframe from scratch if not, and cache it
    - query dataframe for domain

    format of return data:
    {
        "domain": "example.com",
        "signals": [
            {
                "signal_name": "foo",
                "signal_data": {
                    "value": 123,
                }
            },
            {
                "signal_name": "bar",
                "signal_data": {
                    "value": 456,
                }
            }
            . . .
        ]
    },
    """

    # if cache exists for this domain, return that value
    if force_refresh == False and is_cached(domain, CacheType.signals):
        signals = get_cache(domain, CacheType.signals)
        return {
            "retrieved_from_cache": True,
            "signals": signals
        }

    # else go and retrieve signal info for domain and then save in cache

    # ensure Wiki Signal data is available
    try:
        df_signal_data = load_signal_data()

    except Exception as e:
        raise IariFetchError(f"Problem fetching raw wiki signal data ({str(e)})")

    # Find matching domain record
    domain_record = df_signal_data[df_signal_data['domain'] == domain]

    # return error if not found
    if len(domain_record) == 0:
        return {
            "error": f"No signal data found for domain: {domain}"
        }

    # Extract first matching record
    record = domain_record.iloc[0]

    # Format signal data
    signals = []
    for col in record.index:
        if col != 'domain':  # Skip domain column
            def convert_to_json_safe(val):
                if pd.isna(val):
                    return None
                elif isinstance(val, bool):
                    return int(val)
                elif isinstance(val, (int, float)):
                    if pd.isna(val):
                        return None
                    return val
                return str(val)

            value = convert_to_json_safe(record[col])
            signals.append({
                "signal_name": col,
                "signal_data": {
                    "value": value
                }
            })

    # save signals in cache for this domain
    set_cache(domain, CacheType.signals, payload=signals)

    # return signal data for this domain
    return {
        "signals" : signals
    }


def filter_signal_data(signals, filters="remove_nulls"):
    """
    Filters signal records to remove entries with null, False or empty array values.

    Parameters:
        signals (list): List of signal dictionaries containing signal_name and signal_data
        filters (str): Filter type to apply, currently only supports "remove_nulls"

    Returns:
        dict: Dictionary containing filtered signals where signal_data.value is not null,
              False or empty array
    """

    if filters == "remove_nulls":
        filtered_signals = []
        for signal in signals:
            value = signal.get("signal_data", {}).get("value")
            # Check various null/empty conditions
            if (value is not None  # Skip None values (includes null)
                    and value is not False  # Skip boolean False
                    and not (isinstance(value, list) and len(value) == 0)  # Skip empty lists
                    # and value != []  # Skip empty lists
                    and value != "False"  # Skip string "False"
                    and value != "[]"  # Skip string "[]"
            ):
                filtered_signals.append(signal)
        
    else:
        filtered_signals = signals

    # turn filtered signals array into dict
    signals_dict = {
        signal["signal_name"]: signal["signal_data"]["value"]
        for signal in filtered_signals
    }

    # If no valid filter specified, return original signals
    return signals_dict
