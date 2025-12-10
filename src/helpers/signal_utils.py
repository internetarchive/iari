import pandas as pd
import pickle
import config

SIGNALS_CACHE_DIR = f"{config.iari_cache_dir}cache"
SIGNALS_CSV = config.iari_cache_dir

def get_signal_data_for_domain(domain, force_refresh=False):
    """
    grabs signal data for job.domain from Wiki Signal data

    use job.domain as key to extract data from "database"
    - get dataframe
        - get cached dataframe file from disk if there (parquet? csv?)
        - create dataframe from scratch if not, and cache it
    - query dataframe for domain

    for now, grab from local cache, but eventually will grab from API

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

        ]
    },
    """

    def load_signal_data(force_refresh=False):

        # pull from cache if there...
        import os
        os.makedirs(SIGNALS_CACHE_DIR, exist_ok=True)
        cache_path = os.path.join(SIGNALS_CACHE_DIR, f"wiki_signals.pickle")

        from src import app
        app.logger.debug(f"==> load_signal_data:: cache_path is {cache_path}, force_refresh = {force_refresh}")

        # ✅ Step 1: Load from cache if exists and not forcing refresh
        if not force_refresh and os.path.exists(cache_path):
            app.logger.debug(f"Loading wiki_signal data from cache...")
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

    try:
        df_signal_data = load_signal_data()

    except Exception as e:
        raise IariFetchError(f"Problem fetching raw wiki signal data ({str(e)})")

    # Find matching domain record
    domain_record = df_signal_data[df_signal_data['domain'] == domain]

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

    return { "signals" : signals }