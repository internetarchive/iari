# iari_utils.py

def iari_errors(e:Exception):
    return { "errors": [
                {
                    "error": type(e).__name__,
                    "details": str(e),
                },
            ]}

import tldextract

def iari_extract_root_domain(url: str) -> str:
    """
    Returns the registered domain (e.g., example.com, example.co.uk)
    from any URL or hostname.
    """
    # tldextract handles raw hostnames, messy URLs, with or without scheme
    ext = tldextract.extract(url)

    if not ext.domain or not ext.suffix:
        return None  # no valid domain found

    return f"{ext.domain}.{ext.suffix}"


if __name__ == "__main__":
    print("iari_utils")


