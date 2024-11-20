import requests
from datetime import datetime

def get_current_timestamp():
    now = datetime.utcnow()
    return now.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_wikipedia_article(domain, title, timestamp):
    url = f"https://{domain}/w/api.php"
    continue_token = None

    # Query for revisions, and stop once the target revision is found
    while True:
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": title,
            "rvlimit": "max",
            "rvprop": "ids|timestamp",
            "rvdir": "older"
        }
        if continue_token:
            params["rvcontinue"] = continue_token
        response = requests.get(url, params=params)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if "missing" in page_info:
                return None, None, None, None  # Article did not exist at the given time
            revisions = page_info.get("revisions", [])
            # Check each revision to find the target one
            for rev in revisions:
                try:
                    rev_timestamp = rev["timestamp"]
                    if rev_timestamp <= timestamp:
                        # Fetch the content of the identified revision
                        revision_id = rev["revid"]
                        content_params = {
                            "action": "query",
                            "format": "json",
                            "prop": "revisions",
                            "revids": revision_id,
                            "rvprop": "content"
                        }
                        content_response = requests.get(url, params=content_params)
                        content_data = content_response.json()
                        # Extract content
                        for page_id, page_info in content_data.get("query", {}).get("pages", {}).items():
                            content_revisions = page_info.get("revisions", [])
                            if content_revisions:
                                return page_id, revision_id, rev_timestamp, content_revisions[0]["*"]
                        return None, None, None, None
                except KeyError:  # Caused by deleted revision
                    continue
        continue_token = data.get("continue", {}).get("rvcontinue")
        if not continue_token:
            break
    # Return None if no suitable revision was found
    return None, None, None, None

if __name__ == "__main__":
    print(get_wikipedia_article("en.wikipedia.org", "Easter_Island", "2003-01-01T00:00:00Z"))
