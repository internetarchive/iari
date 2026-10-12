# IARI API Documentation

This document covers the IARI endpoints implemented in `src/views/v2`, along with
their request schemas (`src/models/v2/schema`) and job models (`src/models/v2/job`).
Legacy endpoints (`/statistics/*`, `/check-urls`, `/check-doi`, `/check-url-archive`)
are intentionally excluded.

Current version: **4.5.5** (from `pyproject.toml`).

---

## Contents

- [General conventions](#general-conventions)
- [Endpoint summary](#endpoint-summary)
- Service
  - [/help](#help)
  - [/version](#version)
- Reference extraction
  - [/extract_refs](#extract_refs)
  - [/extract_grok](#extract_grok)
  - [/fetchrefs](#fetchrefs)
  - [/refs_lookup](#refs_lookup)
  - [/editref](#editref)
  - [/get_book_reference](#get_book_reference)
- Articles
  - [/article](#article)
  - [/article_cache](#article_cache)
- URLs and sources
  - [/check-url](#check-url)
  - [/get_url_info](#get_url_info)
  - [/probe](#probe)
  - [/signals](#signals)
  - [/wiki_signals](#wiki_signals)
  - [/signals_docs](#signals_docs)
- Insights
  - [/insights, /webrx_insights](#insights--webrx_insights)
  - [/tarb_insights](#tarb_insights)
  - [/wiki_insights](#wiki_insights)
- [Code structure (v2)](#code-structure-v2)
- [Known issues and caveats](#known-issues-and-caveats)

---

## General conventions

### Base URL

All routes are registered under the `/v2` prefix (`src/__init__.py`):

```
https://<host>/v2/<endpoint>
```

### Request parameters

- **GET** requests take parameters from the query string.
- **POST** requests take parameters from **form data** (`application/x-www-form-urlencoded`
  or `multipart/form-data`). JSON request bodies are **not** read.
- Parameters are validated with marshmallow. **Unknown parameters are rejected**:
  passing a parameter the endpoint's schema does not define returns a validation error.
- Boolean parameters accept marshmallow's truthy/falsy strings, e.g. `true`/`false`, `1`/`0`,
  `yes`/`no`, `on`/`off`.
- Pipe-delimited list parameters (`pages`, `probes`, `parts`) use `|` as the separator,
  e.g. `probes=verifyi|trust_project`.

### Common parameters

Most v2 endpoints inherit from `BaseSchemaV2` (`src/models/v2/schema/__init__.py`)
and therefore accept these optional parameters in addition to their own:

| Parameter  | Type    | Description |
|------------|---------|-------------|
| `refresh`  | bool    | Ignore any cached result, fetch fresh data, and re-cache it. |
| `testing`  | bool    | Testing mode. For some endpoints, skips writing results to the cache. |
| `hydrate`  | bool    | Return extra/expanded detail where an endpoint supports it. |
| `tag`      | string  | Pass-through value echoed back in some responses to help identify the request. |
| `timeout`  | int ≥ 0 | Timeout in seconds for outbound requests, where used. |
| `showall`  | bool    | Accepted, currently unused. |
| `uselocal` | bool    | Accepted, currently unused. |

Exceptions: `/check-url` and `/get_url_info` use the older `BaseSchema`, which only
provides `refresh` and `testing` (plus their own parameters). `/help` takes no parameters.

### Errors

Validation failures and runtime errors return HTTP **500** with one of these bodies,
depending on the endpoint:

```json
{ "error": "Missing Information Error: {'page_title': ['Missing data for required field.']}" }
```

```json
{ "errors": [ { "error": "MissingInformationError", "details": "page_title or wikitext must be specified" } ] }
```

The second (`errors` array) form is used by `/extract_refs` and `/extract_grok`.
Unhandled exceptions are caught by the app-level handler and return 500 with an
`errors` array. Unknown routes return `{"error": "Endpoint '<path>' not found"}`.

### Common response fields

Many endpoints include some of the following metadata:

| Field            | Description |
|------------------|-------------|
| `iari_version`   | IARI version string from `pyproject.toml`. |
| `iari_command`   | Name of the command that produced the response. |
| `endpoint`       | Flask endpoint name that handled the request. |
| `execution_time` | Processing time, formatted like `"1.2345 seconds"`. |
| `timestamp`      | Unix timestamp (int) or `YYYY-MM-DD HH:MM:SS` string, depending on endpoint. |
| `isodate`        | ISO 8601 date/time of the response. |

---

## Endpoint summary

| Route | Methods | Purpose |
|-------|---------|---------|
| [`/help`](#help) | GET | Basic API help. |
| [`/version`](#version) | GET | IARI version and host info. |
| [`/extract_refs`](#extract_refs) | GET, POST | Extract references, URLs and cite-refs from a Wikipedia article. **Preferred extraction endpoint.** |
| [`/extract_grok`](#extract_grok) | GET, POST | Extract URLs from a Grokipedia article. |
| [`/fetchrefs`](#fetchrefs) | GET, POST | Fetch raw reference wikitext for one or more English Wikipedia pages. |
| [`/refs_lookup`](#refs_lookup) | GET, POST | Look up a URL in the Wikipedia Citations Database. |
| [`/editref`](#editref) | GET, POST | Replace a reference string in wikitext and return the result. |
| [`/get_book_reference`](#get_book_reference) | GET, POST | Book reference lookup (placeholder). |
| [`/article`](#article) | GET | Full analysis and statistics for a Wikipedia article. |
| [`/article_cache`](#article_cache) | GET | Return a previously cached article analysis by IARI id. |
| [`/check-url`](#check-url) | GET | Check the live status of a URL. |
| [`/get_url_info`](#get_url_info) | GET | Combined URL information by "parts" (in development). |
| [`/probe`](#probe) | GET | Run reliability probes against a URL. |
| [`/signals`](#signals) | GET | WikiSignals data for a domain or URL. |
| [`/wiki_signals`](#wiki_signals) | GET | WikiSignals data for a domain, wrapped per domain. |
| [`/signals_docs`](#signals_docs) | GET | WikiSignals signal definitions. |
| [`/insights`, `/webrx_insights`](#insights--webrx_insights) | GET | Wayback link statistics (WebRx / botwikiawk dashboard). |
| [`/tarb_insights`](#tarb_insights) | GET | IABot (TARB) statistics summary. |
| [`/wiki_insights`](#wiki_insights) | GET | Wikipedia external-URL statistics. |

---

## Service

### /help

`GET /v2/help`

Returns a summary of every v2 endpoint. No parameters.

**View:** `src/views/v2/help_v2.py` (`HelpV2`)

```json
{
  "name": "IARI API",
  "description": "Help endpoint for available API routes and basic usage.",
  "base_path": "/v2",
  "documentation": "https://github.com/internetarchive/iari/blob/main/docs/IARI.documentation.md",
  "common_parameters": { "refresh": "bool - ...", "testing": "...", "hydrate": "...", "tag": "...", "timeout": "..." },
  "endpoints": {
    "/version": { "method": "GET", "description": "Returns the current IARI API version." },
    "/extract_refs": {
      "method": "GET, POST",
      "description": "Extracts references, URLs, section names and cite-refs from a Wikipedia article.",
      "parameters": { "page_title": "required - article title", "...": "..." }
    },
    "...": "one entry per route"
  }
}
```

The `parameters` object is included for endpoints that take endpoint-specific parameters.

---

### /version

`GET /v2/version`

Returns the running IARI version and server information.

**View:** `version_v2.py` (`VersionV2`) · **Schema:** `VersionSchemaV2` · **Job:** `VersionJobV2`

**Parameters:** common parameters only.

**Response:**

```json
{
  "version": "4.5.5",
  "timestamp": 1760140800,
  "isodate": "2026-10-11T00:00:00.000000",
  "host": "iari.example.org",
  "hash_test": { "key": "free.speech.forever", "hash": "<cache hash>" }
}
```

`hash_test` shows the cache-key hash for a fixed string, so you can check that cache
hashing behaves the same across deployments.

---

## Reference extraction

### /extract_refs

`GET | POST /v2/extract_refs`

Extracts all references (`<ref>` tags), URLs, section names and cite-ref anchors from
a Wikipedia article, optionally as of a given point in time. Based on James Hare's
extraction code. This is the preferred reference extraction endpoint.

**View:** `extract_refs_v2.py` (`ExtractRefsV2`) · **Schema:** `ExtractRefsSchemaV2` ·
**Job:** `ExtractRefsJobV2` · **Analyzer:** `src/models/v2/analyzers/wiki_analyzer.py`

**Parameters:**

| Parameter    | Type   | Required | Default            | Description |
|--------------|--------|----------|--------------------|-------------|
| `page_title` | string | yes\*    | `""`               | Article title, e.g. `Easter Island`. Spaces are converted to underscores. |
| `domain`     | string | no       | `en.wikipedia.org` | Wiki host to fetch from. |
| `as_of`      | string | no       | now                | Fetch the revision current as of this ISO 8601 timestamp, e.g. `2024-01-01T00:00:00Z`. |
| `wikitext`   | string | no\*     | `""`               | Accepted by the schema, but not used for extraction yet (see [caveats](#known-issues-and-caveats)). |
| `hydrate`    | bool   | no       | `false`            | Adds `claim_array` and `hydrate: true` to each reference. |

\* Either `page_title` or `wikitext` is required. In practice, `page_title` is needed.

**Example:**

```
GET /v2/extract_refs?page_title=Easter_Island&as_of=2024-01-01T00:00:00Z
```

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "extract_refs",
  "page_errors": null,
  "execution_time": "2.1043 seconds",
  "hydrate": false,
  "media_type": "wiki_article",
  "page_title": "Easter_Island",
  "domain": "en.wikipedia.org",
  "as_of": "2024-01-01T00:00:00Z",
  "page_id": "9692",
  "revision_id": "1192785042",
  "section_names": ["", "Etymology", "History", "..."],
  "url_count": 210,
  "urls": ["https://...", "..."],
  "reference_count": 180,
  "references": [
    {
      "wikitext": "<ref name=\"foo\">{{cite web |url=... |title=...}}</ref>",
      "name": "foo",
      "urls": ["https://..."],
      "section": "History",
      "templates": [ { "name": "cite web", "parameters": { "url": "...", "title": "..." } } ],
      "template_names": ["cite web"],
      "titles": ["..."],
      "claim": "Text in the article that precedes this reference."
    }
  ],
  "cite_refs_count": 220,
  "cite_refs": [ "..." ]
}
```

- `urls` is the de-duplicated set of URLs found across all references.
- `cite_refs` comes from the article's rendered HTML (`iarilib` `extract_cite_refs`) and
  maps the in-text citation anchors to their references.
- `{{sfn}}` short-footnote templates are not yet extracted as references.

---

### /extract_grok

`GET | POST /v2/extract_grok`

Extracts URLs from a [Grokipedia](https://grokipedia.com) article.

**View:** `extract_grok_v2.py` (`ExtractGrokV2`) · **Schema:** `ExtractGrokSchemaV2` ·
**Job:** `ExtractGrokJobV2` · **Analyzer:** `src/models/v2/analyzers/grok_analyzer.py`

**Parameters:**

| Parameter         | Type   | Required | Default | Description |
|-------------------|--------|----------|---------|-------------|
| `page_title`      | string | yes      |         | Grokipedia page title. Fetched from `https://grokipedia.com/page/<page_title>`. |
| `use_local_cache` | bool   | no       | `false` | Read the page HTML from the local cache directory (`config.iari_cache_local_dir`) instead of the live site. |

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "extract_grok",
  "page_errors": null,
  "timestamp": "2026-10-11 12:00:00",
  "execution_time": "0.8120 seconds",
  "use_local_cache": false,
  "media_type": "grokipedia_article",
  "page_title": "Easter_Island",
  "url_count": 42,
  "urls": ["https://...", "..."],
  "url_dict": { "...": "..." }
}
```

If fetching or parsing fails, the endpoint still returns 200. The error message is
placed in `page_errors` and the data fields are `null`.

---

### /fetchrefs

`GET | POST /v2/fetchrefs`

Fetches the raw reference wikitext for one or more English Wikipedia pages.

**View:** `fetchrefs_v2.py` (`FetchRefsV2`) · **Schema:** `FetchRefsSchemaV2` · **Job:** `FetchRefsJobV2`

**Parameters:**

| Parameter    | Type   | Required | Default  | Description |
|--------------|--------|----------|----------|-------------|
| `pages`      | string | yes\*    |          | Pipe-delimited list of page titles, e.g. `Easter_Island\|Moai`. |
| `which_wiki` | string | no       | `enwiki` | Echoed back in the response. Pages are always fetched from `en.wikipedia.org`. |
| `wikitext`   | string | no\*     |          | Accepted, but not processed yet. |

\* Either `pages` or `wikitext` is required.

**Response:**

```json
{
  "pages": [
    {
      "page_title": "Easter_Island",
      "which_wiki": "enwiki",
      "refs": [
        { "name": "foo", "wikitext": "<ref name=\"foo\">...</ref>" }
      ]
    },
    {
      "page_title": "No_Such_Page",
      "which_wiki": "enwiki",
      "error": "Page data error: ..."
    }
  ]
}
```

Errors for individual pages are reported in that page's entry. They don't fail the whole request.

---

### /refs_lookup

`GET | POST /v2/refs_lookup`

Looks up a URL in James Hare's Wikipedia Citations Database
(`https://wikipediacitations.scatter.red/`) and returns the Wikipedia references that cite it.

**View:** `refs_lookup_v2.py` (`RefsLookupV2`) · **Schema:** `RefsLookupSchemaV2` · **Job:** `RefsLookupJobV2`

**Parameters:**

| Parameter | Type   | Required | Default | Description |
|-----------|--------|----------|---------|-------------|
| `url`     | string | yes      |         | The cited URL to look up (non-empty). |
| `raw`     | bool   | no       | `false` | Return raw reference wikitext. |
| `output`  | string | no       | `JSON`  | `JSON`, `HTML` or `TSV` (case-insensitive). `TSV` cannot be combined with `raw=true`. |

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "refs_lookup",
  "execution_time": "0.5021 seconds",
  "url": "https://example.com/article",
  "use_raw": false,
  "refs": { "...": "data returned by the citations database" }
}
```

If the citations database returns a non-200 status, `refs` is
`{"status": "NOT OK", "data": ["got bad response from json fetch for refs lookup"]}`.

---

### /editref

`GET | POST /v2/editref`

Replaces every occurrence of `old_ref` with `new_ref` in some wikitext and returns the
edited wikitext. The source is either supplied directly or fetched from a Wikipedia page.
The endpoint does **not** save anything to Wikipedia.

**View:** `editref_v2.py` (`EditRefV2`) · **Schema:** `EditRefSchemaV2` · **Job:** `EditRefJobV2`

**Parameters:**

| Parameter       | Type   | Required | Description |
|-----------------|--------|----------|-------------|
| `old_ref`       | string | yes      | Exact text to find. |
| `new_ref`       | string | yes      | Replacement text. |
| `source`        | string | yes\*    | Wikitext to edit. Takes precedence over `wiki_page_url`. |
| `wiki_page_url` | string | yes\*    | Full article URL, e.g. `https://en.wikipedia.org/wiki/Easter_Island`. The current wikitext is fetched from the MediaWiki REST API. |

\* Either `source` or `wiki_page_url` is required.

Use POST for large `source` values.

**Response:** the edited wikitext as a JSON string. Error responses use the standard
`{"error": "..."}` shape.

---

### /get_book_reference

`GET | POST /v2/get_book_reference`

Placeholder for returning a book snippet for a book reference. It currently returns
hard-coded data.

**View:** `get_book_reference_v2.py` (`GetBookReferenceV2`) · **Schema:** `GetBookReferenceSchemaV2` ·
**Job:** `GetBookReferenceJobV2`

**Parameters:**

| Parameter  | Type   | Required | Description |
|------------|--------|----------|-------------|
| `book_ref` | string | yes      | Book reference to look up. |

**Response (fixed):**

```json
{ "title": "A Book", "pages": "238", "image": "ABCDEFGBASE64GOBLYGOOKGOESHERE" }
```

---

## Articles

### /article

`GET /v2/article`

Fetches, parses and analyzes a Wikipedia article. Returns article metadata, reference
statistics, references and URLs. Results are cached on disk (subfolder `articlesV2/`)
under the article's IARI id, `<lang>.<site>.<page_id>.<revision_id>`.

**View:** `article_view_v2.py` (`ArticleV2`) · **Schema:** `ArticleSchemaV2` · **Job:** `ArticleJobV2` ·
**Analyzer:** `src/models/v2/wikimedia/wikipedia/analyzer_v2.py` (`WikipediaAnalyzerV2`)

**Parameters:**

| Parameter         | Type   | Required | Description |
|-------------------|--------|----------|-------------|
| `url`             | string | yes      | Full article URL, e.g. `https://en.wikipedia.org/wiki/Easter_Island`. Language, site and title are parsed from it. |
| `reference_types` | string | no       | Accepted, currently unused. |
| `url_details`     | bool   | no       | Accepted, currently unused. |
| `url_method`      | string | no       | Accepted, currently unused. |
| `refresh`         | bool   | no       | Skip the cache and re-analyze. |
| `testing`         | bool   | no       | Don't write the result to the cache. |

**Example:**

```
GET /v2/article?url=https://en.wikipedia.org/wiki/Easter_Island
```

**Response** (`ArticleStatisticsV2`, `src/models/v2/statistics/article_stats_v2.py`):

```json
{
  "iari_version": "4.5.5",
  "iari_id": "en.wikipedia.org.9692.1192785042",
  "page_errors": [],
  "lang": "en",
  "site": "wikipedia.org",
  "title": "Easter_Island",
  "page_id": 9692,
  "revision_id": 1192785042,
  "revision_isodate": "2024-01-01T00:00:00+00:00",
  "revision_timestamp": 1704067200,
  "served_from_cache": false,
  "isodate": "2026-10-11T12:00:00.000000",
  "timestamp": 1760184000,
  "execution_time": 3,
  "ores_score": {},
  "reference_count": 180,
  "reference_stats": { "...": "..." },
  "references": [ { "...": "..." } ],
  "url_count": 210,
  "url_stats": { "...": "..." },
  "urls": ["https://..."]
}
```

**Status codes:**

| Code | Meaning |
|------|---------|
| 200  | Success (fresh or cached). |
| 400  | Title missing, unsupported site, or the page is a redirect. |
| 404  | Article not found. |
| 500  | Wikipedia API or other error. |

---

### /article_cache

`GET /v2/article_cache`

Returns a previously cached article analysis by IARI id, without fetching anything.

**View:** `article_cache_view_v2.py` (`ArticleCacheV2`) · **Schema:** `ArticleCacheSchemaV2` ·
**Job:** `ArticleCacheJobV2`

**Parameters:**

| Parameter         | Type   | Required | Default | Description |
|-------------------|--------|----------|---------|-------------|
| `iari_id`         | string | yes      |         | IARI id, e.g. `en.wikipedia.org.9692.1192785042`. |
| `article_version` | int    | no       | `1`     | `1` = original article format, `2` = V2 format. Currently not used for the lookup. |

**Response:** the cached article JSON with status 200, or `null` if nothing is cached
under that id. This endpoint reads from the `articles/` cache subfolder (the original
`/statistics/article` cache), not from `articlesV2/`.

---

## URLs and sources

### /check-url

`GET /v2/check-url`

Checks the live status of a URL and returns status and parsing information. Results
are cached per URL and method.

**View:** `check_url_v2.py` (`CheckUrlV2`) · **Schema:** `CheckUrlSchemaV2` · **Job:** `CheckUrlJobV2`

**Parameters:**

| Parameter | Type   | Required | Default        | Description |
|-----------|--------|----------|----------------|-------------|
| `url`     | string | yes      |                | URL to check (URL-encode it). |
| `method`  | string | no       | `LIVEWEBCHECK` | `LIVEWEBCHECK`, `IABOT` or `CORENTIN`. `WAYBACK` and `LWC` are aliases for `LIVEWEBCHECK`. Case-insensitive. |
| `timeout` | int    | no       | `2`            | Request timeout in seconds. |
| `refresh` | bool   | no       | `false`        | Bypass the cache. |
| `testing` | bool   | no       | `false`        | Don't write the result to the cache. |

**Response:** the URL check result from `src/models/identifiers_checking/url.py`
(`Url.get_dict`), plus:

| Field           | Description |
|-----------------|-------------|
| `id`            | 8-character id: the first 8 characters of the MD5 hash of the upper-cased URL. Also the cache key. |
| `timestamp`     | Unix timestamp of the check. |
| `isodate`       | ISO date of the check. |
| `refreshed_now` | `true` if `refresh` was requested. |

The `text` field (page content) is returned in fresh responses but is not stored in the
cache, so cached responses don't include it.

---

### /get_url_info

`GET /v2/get_url_info`

Combined URL information endpoint that returns selected "parts". **In development:**
parts currently return placeholders only.

**View:** `get_url_info_v2.py` (`GetUrlInfoV2`) · **Schema:** `GetUrlInfoSchemaV2` · **Job:** `GetUrlInfoJobV2`

**Parameters:**

| Parameter       | Type   | Required | Default               | Description |
|-----------------|--------|----------|-----------------------|-------------|
| `url`           | string | yes      |                       | URL to describe. |
| `parts`         | string | no       | `status\|probes\|test` | Pipe-delimited list of parts to return. |
| `probes`        | string | no       |                       | Pipe-delimited probe names (not yet used). |
| `status_method` | string | no       |                       | Accepted, not yet used. |
| `timeout`       | int    | no       | `2`                   | Timeout in seconds. |

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "get_url_info",
  "endpoint": "geturlinfov2",
  "timestamp": 1760184000,
  "isodate": "2026-10-11T12:00:00.000000",
  "execution_time": "0.0001 seconds",
  "url": "https://example.com",
  "parts_list": ["status", "probes"],
  "probe_list": [],
  "parts": {
    "status": { "part_name": "status" },
    "probes": { "part_name": "probes" }
  }
}
```

Unrecognized parts (including `test`, which is in the default list) come back as
`{"errors": ["Unknown part: <name>"]}`.

---

### /probe

`GET /v2/probe`

Runs one or more reliability probes against a URL. Probe results are cached per URL and probe.

**View:** `probe_v2.py` (`ProbeV2`) · **Schema:** `ProbeSchemaV2` · **Job:** `ProbeJobV2` ·
**Probes:** `src/models/v2/probes/`

**Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `url`     | string | yes      | URL to probe. |
| `probe`   | string | yes\*    | A single probe name. |
| `probes`  | string | yes\*    | Pipe-delimited list of probe names. |
| `refresh` | bool   | no       | Re-run the probes and update the cache. |
| `tag`     | string | no       | Echoed back in the response. |
| `timeout` | int    | no       | Timeout in seconds (default `2`). |

\* Specify exactly one of `probe` or `probes`. Specifying both is an error.

**Available probes** (case-insensitive):

| Probe           | Implementation |
|-----------------|----------------|
| `verifyi`       | `probe_verifyi.py` |
| `trust_project` | `probe_trust_project.py` |
| `test`          | `probe_test.py` |

**Example:**

```
GET /v2/probe?url=https://www.bbc.com/news&probes=verifyi|trust_project
```

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "probe",
  "endpoint": "probev2",
  "timestamp": 1760184000,
  "isodate": "2026-10-11T12:00:00.000000",
  "tag": "optional",
  "execution_time": "0.7342 seconds",
  "url": "https://www.bbc.com/news",
  "probe_list": ["verifyi", "trust_project"],
  "probe_results": {
    "verifyi": { "...": "..." },
    "trust_project": { "...": "..." }
  }
}
```

An unknown probe name returns `{"errors": ["Unknown probe: <name>"]}` in its
`probe_results` entry.

---

### /signals

`GET /v2/signals`

Returns [WikiSignals](https://wikisignals.org) data for a domain. Results are cached per domain.

**View:** `signals_v2.py` (`SignalsV2`) · **Schema:** `SignalsSchemaV2` · **Job:** `SignalsJobV2`

**Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `domain`  | string | yes\*    | Domain, e.g. `nytimes.com`. |
| `url`     | string | yes\*    | Any URL. Its registered domain is extracted (via `tldextract`) when `domain` is not given. |
| `refresh` | bool   | no       | Bypass the cache. |
| `tag`     | string | no       | Echoed back in the response. |

\* Either `domain` or `url` is required. `domain` takes precedence.

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "signals",
  "endpoint": "signalsv2",
  "timestamp": 1760184000,
  "isodate": "2026-10-11T12:00:00.000000",
  "execution_time": "0.3011 seconds",
  "url": "https://www.nytimes.com/some/article",
  "domain": "nytimes.com",
  "signal_data": {
    "retrieved_from_cache": true,
    "signals": { "...": "WikiSignals API response" }
  }
}
```

`retrieved_from_cache` is present only when the data came from the cache. If the
WikiSignals API call fails, `signals` is `{}`.

---

### /wiki_signals

`GET /v2/wiki_signals`

Returns WikiSignals data for a domain, keyed by domain. Similar to `/signals`, but always
reads from the cache when available and requires `domain`.

**View:** `wiki_signals_v2.py` (`WikiSignalsV2`) · **Schema:** `WikiSignalsSchemaV2` · **Job:** `WikiSignalsJobV2`

**Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `domain`  | string | yes      | Domain, e.g. `wikipedia.org`. |

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "wiki_signals",
  "endpoint": "wikisignalsv2",
  "timestamp": "2026-10-11 12:00:00",
  "execution_time": "0.2100 seconds",
  "domains": {
    "wikipedia.org": {
      "debug": { "domain": "wikipedia.org" },
      "synopsis": "Signal data for wikipedia.org",
      "signals": { "signals": { "...": "..." } }
    }
  }
}
```

---

### /signals_docs

`GET /v2/signals_docs`

Returns the WikiSignals signal definitions
(`https://wikisignals.org/wp-json/publications/v1/domain/?view=definitions`). Cached.

**View:** `signals_docs_v2.py` (`SignalsDocsV2`) · **Schema:** `SignalsDocsSchemaV2` · **Job:** `SignalsDocsJobV2`

**Parameters:** common parameters only (`refresh` bypasses the cache, `tag` is echoed back).

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "signals_docs",
  "endpoint": "signalsdocsv2",
  "timestamp": 1760184000,
  "isodate": "2026-10-11T12:00:00.000000",
  "execution_time": "0.1500 seconds",
  "data": {
    "retrieved_from_cache": true,
    "signals_docs": { "...": "definitions" }
  }
}
```

---

## Insights

All three insights endpoints accept `date_start` and `date_end` (optional strings),
but none of them use these yet. Each returns the whole available dataset.

### /insights, /webrx_insights

`GET /v2/insights` · `GET /v2/webrx_insights` (aliases for the same resource)

Wayback Machine link statistics, scraped from the botwikiawk yearly dashboard
(`https://tools-static.wmflabs.org/botwikiawk/dashyearly.html`).

**View:** `insights_webrx_v2.py` (`InsightsWebRxV2`) · **Schema:** `InsightsWebRxSchemaV2` ·
**Job:** `InsightsWebRxJobV2`

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "insights",
  "endpoint": "insightswebrxv2",
  "execution_time": "1.0200 seconds",
  "execution_errors": null,
  "webrx": {
    "table_names": ["Wayback by IABot", "Wayback by Users", "Wayback by User Bots", "LAMP", "LAMP SIM", "Media by Users"],
    "table_totals": {
      "column_names": ["2016", "2017", "..."],
      "tables": [ { "name": "Wayback by IABot", "cols": [123, 456], "total": 579 } ]
    },
    "tables": [
      {
        "name": "Wayback by IABot",
        "column_names": ["2016", "2017", "..."],
        "column_totals": [123, 456],
        "rows": [ { "#": "1", "site": "enwiki", "total": "1,234", "cols": ["100", "200"] } ]
      }
    ]
  }
}
```

---

### /tarb_insights

`GET /v2/tarb_insights`

IABot ("Turn All References Blue") edit statistics from
`https://iabot.wmcloud.org/api.php?action=statistics`, loaded year by year from 2022
through the current year. Past years are cached as pickles in `config.iari_cache_dir`.
The current year is always re-fetched.

**View:** `insights_tarb_v2.py` (`InsightsTarbV2`) · **Schema:** `InsightsTarbSchemaV2` ·
**Job:** `InsightsTarbJobV2`

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "tarb_insights",
  "endpoint": "insightstarbv2",
  "execution_time": "4.5000 seconds",
  "execution_errors": null,
  "summary_data": {
    "first_day": "2022-01-01",
    "last_day": "2026-10-10"
  }
}
```

Currently only the date range of the loaded data is summarized.

---

### /wiki_insights

`GET /v2/wiki_insights`

Wikipedia external-link statistics from the Wikimedia Commons dataset
`Data:Wikipedia_statistics/exturls.tab`.

**View:** `insights_wiki_v2.py` (`InsightsWikiV2`) · **Schema:** `InsightsWikiSchemaV2` ·
**Job:** `InsightsWikiJobV2`

**Response:**

```json
{
  "iari_version": "4.5.5",
  "iari_command": "wiki_insights",
  "endpoint": "insightswikiv2",
  "execution_time": "0.9000 seconds",
  "execution_errors": null,
  "external_urls": [ "..." ]
}
```

---

## Code structure (v2)

Each v2 endpoint follows the same pattern:

```
request ──► View (src/views/v2/*_v2.py)
              │  __validate_and_get_job__()
              ▼
            Schema (src/models/v2/schema/*_schema_v2.py)   marshmallow: validates request args
              │  @post_load
              ▼
            Job (src/models/v2/job/*_job_v2.py)            pydantic: typed params + validate_fields()
              │
              ▼
            View logic ──► analyzers / helpers / file_io cache ──► JSON response
```

| Directory | Contents |
|-----------|----------|
| `src/views/v2/` | Flask-RESTful resources, one per endpoint. Most subclass `StatisticsViewV2` (`src/views/v2/statistics/__init__.py`), which reads GET args or POST form data, validates it against `schema`, and loads it into `job`. |
| `src/models/v2/schema/` | Marshmallow request schemas. `BaseSchemaV2` defines the common parameters. |
| `src/models/v2/job/` | Pydantic job models. `JobV2` provides `refresh`, `testing`, `hydrate`, `tag`. `validate_fields()` handles cross-field rules and normalization. |
| `src/models/v2/analyzers/` | `WikiAnalyzerV2` (Wikipedia reference extraction for `/extract_refs`) and `GrokAnalyzerV2` (Grokipedia, for `/extract_grok`). |
| `src/models/v2/wikimedia/wikipedia/` | Article, section, reference and URL models used by `/article` and `/fetchrefs`. |
| `src/models/v2/statistics/` | Pydantic models for article and reference statistics output. |
| `src/models/v2/file_io/` | Disk cache readers/writers (`articlesV2/`, `articles/`, `urls/`, …). |
| `src/models/v2/probes/` | Probe implementations used by `/probe`. |

### Adding an endpoint

1. Create a job in `src/models/v2/job/` that subclasses `JobV2`, with a `validate_fields()` method.
2. Create a schema in `src/models/v2/schema/` that subclasses `BaseSchemaV2`, with a
   `@post_load` that builds the job and calls `validate_fields()`.
3. Create a view in `src/views/v2/` that subclasses `StatisticsViewV2`, sets `schema`,
   and implements `get` and/or `post`.
4. Register it in `src/__init__.py` with `api.add_resource(...)`.
5. Add it to this document and to `/help`.

---

## Known issues and caveats

- **`wikitext` input isn't implemented** for `/extract_refs` and `/fetchrefs`. The schemas
  accept it, but the views still need a page title.
- **`/fetchrefs` only supports English Wikipedia.** `which_wiki` is echoed back but ignored.
- **`/get_url_info` is a stub.** Parts return placeholders, `probes` and `status_method`
  are ignored, and the default `test` part returns an "Unknown part" error.
- **`/get_book_reference` returns hard-coded data.**
- **`/article_cache` reads the v1 `articles/` cache**, not `articlesV2/`. It returns
  `null` (status 200) when nothing is cached. `article_version` is ignored.
- **`/article` ignores `reference_types`, `url_details` and `url_method`.**
- **Insights `date_start`/`date_end` are ignored.**
- **Validation errors return 500** rather than 400.
- **POST reads form data only**, not JSON bodies.
