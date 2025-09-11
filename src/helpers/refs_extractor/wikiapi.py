import requests
from datetime import datetime

import config

wiki_user_agent = (f"IariBot/0.0"
                   f" (https://iabot-api.archive.org/services/context/iari-stage/v2/version; mojomonger@archive.org)"
                   f" iari/0.0")
# wiki_user_agent_2 = "TestBot/0.1 (https://example.com/; test@example.com)"

def get_current_timestamp():
    now = datetime.utcnow()
    return now.strftime('%Y-%m-%dT%H:%M:%SZ')

def make_errors_array(error_name, details):
    return {
        "errors": [
            {
                "error": error_name,
                "details": details,
            }
        ]
    }

def get_wikipedia_article(domain, title, timestamp):
    """
    returns a dict containing article fetch results, or { errors: [] }

    {
        page_id: ,
        rev_id: ,
        rev_timestamp: ,
        wikitext:
    }

        OR

    { errors: [<string>, ...] }

    """

    # TODO make sure domain, title and timestamp are valid,
    #   returning error if not

    endpoint_url = f"https://{domain}/w/api.php"
    continue_token = None

    from src import app

    # Query for revisions, then stop once the target revision is found
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

        headers = {
            "User-Agent": wiki_user_agent
        }

        try:
            # response = requests.get(
            #     endpoint_url,
            #     headers=headers,
            #     params=params,
            #     timeout=6,
            # )
            response = requests.get(
                endpoint_url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()

        except requests.RequestException as e:
            return make_errors_array("Wiki requests error", f"Request failed: {e}")

        try:
            data = response.json()

        except Exception as e:
            app.logger.error(f"wikiapi::get_wikipedia_article: JSON parse error for revisions: {e}.")
            return make_errors_array("Page parsing error", f"JSON parse error for revisions: {e}")

        pages = data.get("query", {}).get("pages", {})
        # TODO error if "pages" does not exist in query
        for page_id, page_info in pages.items():

            # Abort if no page info
            if "missing" in page_info:
                return make_errors_array("Missing page info", f"Article did not exist at the given time")
                # NB TODO Not sure what this means exactly...

            # Check each revision to find the target one
            revisions = page_info.get("revisions", [])
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
                        content_response = requests.get(
                            endpoint_url,
                            params=content_params,
                            headers=headers,
                        )

                        if content_response.status_code != 200:
                            return make_errors_array("Page fetching error",
                                          f"Error fetching data from revision id {revision_id} ({content_response.text})")

                        # NB this should not fail, as we specifically requested JSON format
                        content_data = content_response.json()

                        # Extract content from results
                        for page_id, page_info in content_data.get("query", {}).get("pages", {}).items():
                            content_revisions = page_info.get("revisions", [])
                            if content_revisions:
                                return {
                                    "page_id": page_id,
                                    "rev_id": revision_id,
                                    "rev_timestamp": rev_timestamp,
                                    "wikitext": content_revisions[0]["*"],
                                }

                        # If no content_revisions found, error
                        return make_errors_array("Page content error", f"No content found.")

                except KeyError:  # Caused by deleted revision
                    continue

        continue_token = data.get("continue", {}).get("rvcontinue")
        if not continue_token:
            break

    # Error if no suitable revision found
    return make_errors_array("Page content error", f"No suitable revision found")


if __name__ == "__main__":
    print(get_wikipedia_article("en.wikipedia.org", "Easter_Island", "2003-01-01T00:00:00Z"))
