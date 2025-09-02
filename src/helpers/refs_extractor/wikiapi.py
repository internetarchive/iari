import requests
from datetime import datetime


def get_current_timestamp():
    now = datetime.utcnow()
    return now.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_wikipedia_article(domain, title, timestamp):
    """
    returns {
        page_id: ,
        rev_id: ,
        rev_timestamp: ,
        wikitext:
    }
    or
    {
        errors: [
            <string>, ...
        ]
    }

    """

    from src import app

    endpoint_url = f"https://{domain}/w/api.php"
    continue_token = None

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
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "http://en.wikipedia.org/wiki/User:Iamojo via iabget.awk",
        }

        try:
            response = requests.get(
                endpoint_url,
                headers=headers,
                params=params,
                timeout=6,
            )
            response.raise_for_status()

        except requests.RequestException as e:
            app.logger.error(f"#### get_wikipedia_article request failed: {e}")

            return {
                "errors": [
                    {
                        "error": "Request error",
                        "details": f"get_wikipedia_article request failed: {e}"
                    }
                ]
            }

        try:
            data = response.json()

        except requests.RequestException as e:
            app.logger.error(f"wikiapi::get_wikipedia_article: Bad JSON received for revisions: {e}.")
            return {
                "errors": [
                    {
                        "error": "Page parsing error",
                        "details": f"get_wikipedia_article: Bad JSON received for revisions: {e}"
                    }
                ]
            }

        # TODO error if pages does not exist in query
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():

            if "missing" in page_info:
                return {
                    "errors": [
                        {
                            "error": "Missing page info",
                            "details": "Article did not exist at the given time"
                        }
                    ]
                }

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
                        content_response = requests.get(endpoint_url, params=content_params)
                        app.logger.debug(f"Content response status code: {content_response.status_code}")
                        app.logger.debug(f"Content response headers: {content_response.headers}")
                        app.logger.debug(f"Content response encoding: {content_response.encoding}")
                        app.logger.debug(f"Content response URL: {content_response.url}")
                        app.logger.debug(f"Content response text: {content_response.text}")

                        if content_response.status_code != 200:
                            # except WikipediaApiFetchError as e:
                            #     traceback.print_exc()
                            #     return {"error": f"Wikipedia Api Fetch Error: {str(e)}"}, 500
                            app.logger.debug(f"XXXX XXXX requests failed; returning errors dict")

                            return {
                                "errors": [
                                    {
                                        "error": f"Error fetching response from {endpoint_url}",
                                        "details": content_response.text
                                    }
                                ]
                            }

                        # NB this might fail, but shouldn't, as we requested json format
                        content_data = content_response.json()

                        # Extract content
                        for page_id, page_info in content_data.get("query", {}).get("pages", {}).items():
                            content_revisions = page_info.get("revisions", [])
                            if content_revisions:
                                return {
                                    page_id: page_id,
                                    rev_id: revision_id,
                                    rev_timestamp: rev_timestamp,
                                    wikitext: content_revisions[0]["*"],
                                }
                                # return page_id, revision_id, rev_timestamp, content_revisions[0]["*"]

                        return {
                            "errors": [
                                {
                                    "error": "Page content error",
                                    "details": f"No content found."
                                }
                            ]
                        }

                except KeyError:  # Caused by deleted revision
                    continue

        continue_token = data.get("continue", {}).get("rvcontinue")
        if not continue_token:
            break

    # Error if no suitable revision found
    return {
        "errors": [
            {
                "error": "Page content error",
                "details": f"No suitable revision found"
            }
        ]
    }

if __name__ == "__main__":
    print(get_wikipedia_article("en.wikipedia.org", "Easter_Island", "2003-01-01T00:00:00Z"))
