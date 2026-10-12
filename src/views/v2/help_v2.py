from flask_restful import Resource


class HelpV2(Resource):
    """
    Returns basic help information for the IARI API.
    See docs/IARI.documentation.md for full documentation.
    """

    def get(self):
        return {
            "name": "IARI API",
            "description": "Help endpoint for available API routes and basic usage.",
            "base_path": "/v2",
            "documentation": "https://github.com/internetarchive/iari/blob/main/docs/IARI.documentation.md",
            "common_parameters": {
                "refresh": "bool - ignore cached data and fetch fresh",
                "testing": "bool - testing mode; may skip writing to cache",
                "hydrate": "bool - return expanded detail where supported",
                "tag": "string - pass-through value echoed in some responses",
                "timeout": "int - outbound request timeout in seconds, where used",
            },
            "endpoints": {
                "/help": {
                    "method": "GET",
                    "description": "Returns help information for the API."
                },
                "/version": {
                    "method": "GET",
                    "description": "Returns the current IARI API version."
                },
                "/extract_refs": {
                    "method": "GET, POST",
                    "description": "Extracts references, URLs, section names and cite-refs from a Wikipedia article.",
                    "parameters": {
                        "page_title": "required - article title",
                        "domain": "optional - wiki host (default: en.wikipedia.org)",
                        "as_of": "optional - ISO 8601 timestamp of revision to use (default: now)",
                    },
                },
                "/extract_grok": {
                    "method": "GET, POST",
                    "description": "Extracts URLs from a Grokipedia article.",
                    "parameters": {
                        "page_title": "required - Grokipedia page title",
                        "use_local_cache": "optional - bool, read page HTML from local cache (default: false)",
                    },
                },
                "/fetchrefs": {
                    "method": "GET, POST",
                    "description": "Fetches raw reference wikitext for one or more English Wikipedia pages.",
                    "parameters": {
                        "pages": "required - pipe-delimited list of page titles",
                        "which_wiki": "optional - echoed back (default: enwiki)",
                    },
                },
                "/refs_lookup": {
                    "method": "GET, POST",
                    "description": "Looks up a URL in the Wikipedia Citations Database.",
                    "parameters": {
                        "url": "required - cited URL to look up",
                        "raw": "optional - bool, return raw reference wikitext",
                        "output": "optional - JSON, HTML or TSV (default: JSON); TSV not allowed with raw",
                    },
                },
                "/editref": {
                    "method": "GET, POST",
                    "description": "Replaces old_ref with new_ref in wikitext and returns the edited wikitext. Does not save to Wikipedia.",
                    "parameters": {
                        "old_ref": "required - text to find",
                        "new_ref": "required - replacement text",
                        "source": "source or wiki_page_url required - wikitext to edit",
                        "wiki_page_url": "source or wiki_page_url required - article URL to fetch wikitext from",
                    },
                },
                "/get_book_reference": {
                    "method": "GET, POST",
                    "description": "Book reference lookup (placeholder; returns fixed data).",
                    "parameters": {
                        "book_ref": "required - book reference",
                    },
                },
                "/article": {
                    "method": "GET",
                    "description": "Fetches, analyzes and caches a Wikipedia article, returning statistics, references and URLs.",
                    "parameters": {
                        "url": "required - full article URL, e.g. https://en.wikipedia.org/wiki/Easter_Island",
                    },
                },
                "/article_cache": {
                    "method": "GET",
                    "description": "Returns a previously cached article analysis by IARI id.",
                    "parameters": {
                        "iari_id": "required - e.g. en.wikipedia.org.<page_id>.<revision_id>",
                        "article_version": "optional - 1 or 2 (default: 1)",
                    },
                },
                "/check-url": {
                    "method": "GET",
                    "description": "Checks the live status of a URL.",
                    "parameters": {
                        "url": "required - URL to check",
                        "method": "optional - LIVEWEBCHECK, IABOT or CORENTIN (default: LIVEWEBCHECK)",
                        "timeout": "optional - seconds (default: 2)",
                    },
                },
                "/get_url_info": {
                    "method": "GET",
                    "description": "Combined URL information by parts (in development).",
                    "parameters": {
                        "url": "required - URL to describe",
                        "parts": "optional - pipe-delimited parts (default: status|probes|test)",
                    },
                },
                "/probe": {
                    "method": "GET",
                    "description": "Runs reliability probes against a URL.",
                    "parameters": {
                        "url": "required - URL to probe",
                        "probe": "probe or probes required - single probe name",
                        "probes": "probe or probes required - pipe-delimited probe names (verifyi, trust_project, test)",
                    },
                },
                "/signals": {
                    "method": "GET",
                    "description": "Returns WikiSignals data for a domain.",
                    "parameters": {
                        "domain": "domain or url required - domain name",
                        "url": "domain or url required - URL whose domain is used",
                    },
                },
                "/wiki_signals": {
                    "method": "GET",
                    "description": "Returns WikiSignals data for a domain, keyed by domain.",
                    "parameters": {
                        "domain": "required - domain name",
                    },
                },
                "/signals_docs": {
                    "method": "GET",
                    "description": "Returns WikiSignals signal definitions."
                },
                "/insights": {
                    "method": "GET",
                    "description": "Wayback link statistics from the WebRx dashboard. Alias: /webrx_insights."
                },
                "/webrx_insights": {
                    "method": "GET",
                    "description": "Alias for /insights."
                },
                "/tarb_insights": {
                    "method": "GET",
                    "description": "IABot (TARB) statistics summary."
                },
                "/wiki_insights": {
                    "method": "GET",
                    "description": "Wikipedia external-URL statistics."
                },
            }
        }, 200
