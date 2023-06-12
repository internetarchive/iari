# Internet Archive Reference Inventory [IARI](https://www.wikidata.org/wiki/Q117023013)

This API is capable of fetching, extracting, transforming and storing
reference information from Wikipedia articles as [structured data](https://www.wikidata.org/wiki/Q26813700).

The endpoints make it possible to get structured data about the references 
from any Wikipedia article in any language version.

# Background
There are [at least 200 million references in at least 40 million articles](
https://ieeexplore.ieee.org/abstract/document/9908858)
and together with the article text in the Wikipedias
one of the most valuable collections of knowledge ever made by humans,
see [size comparison](https://en.wikipedia.org/wiki/Wikipedia:Size_comparisons).

Wikimedia movement currently does not have good and effective tools 
to help editors keep up the quality of references over time. 
The references are stored in templates that differ between language versions of Wikipedia 
which makes it hard for tool developers to develop good tools that work well 
across different language versions.

# Author
IARI has been developed by [Dennis Priskorn](https://www.wikidata.org/wiki/Q111016131) as part of the
[Turn All References Blue project](https://www.wikidata.org/wiki/Q115136754) which is led by
Mark Graham, head of The
[Wayback Machine](https://www.wikidata.org/wiki/Q648266) department of the
[Internet Archive](https://www.wikidata.org/wiki/Q461). 

# Goals
The endpoint providing a detailed analysis of a Wikipedia article and it's references
enable wikipedians to get an overview of the state of the references and using the API it is
possible for the Wikimedia tech-community to build tools that help make it easier to curate 
and improve the references.

This is part of a wider initiative help raise the quality of references in
Wikipedia to enable everyone in the world to make decisions
based on trustworthy knowledge
that is derived from trustworthy sources.

# Stepping stone for a (graph) database of all references 
This project is a part of the [Wikicite initiative](http://wikicite.org/).

On the longer term Turn All References Blue project is planning on populating a database
based on the data we extract. 
This part of the effort is led by [James Hare](https://www.wikidata.org/wiki/Q23041486).

The end goal is a large database with all references from all Wikipedias. 
We call it the Wikipedia Citations Database (WCD).

# Features

IARI features a number of endpoints that help patrons
get structured data about references in a Wikipedia article:

* an _article_ endpoint which analyzes a given article and returns basic statistics about it
* a _references_ endpoint which gives back all ids of references found
* a _reference_ endpoint which gives back all details about a reference including templates and wikitext
* a _check-url_ endpoint which looks up the URL and gives back
  standardized information about its status
* a _check-doi_ endpoint which looks up the DOI and gives back
  standardized information about it from [FatCat](https://fatcat.wiki/), OpenAlex and Wikidata
  including abstract, retracted status, and more.
* a _pdf_ endpoint which extracts links both from annotations and free text from PDFs.
* a _xhtml_ endpoint which extracts links both from any XHTML-page.

# Limitations

See known limitations under each endpoint below.

# Supported Wikipedias

Currently we support a handful of the 200+ language versions of Wikipedia
but we plan on extending the support to all Wikipedia language versions
and you can help us by submitting sections to search for references in issues and
pull requests.

We also would like to support non-Wikimedia wikis using MediaWiki in the future
and perhaps also any webpage on the internet with outlinks (e.g. news articles).

## Wikipedia templates

English Wikipedia for example has hundreds of special reference templates in use
and a handful of widely used generic templates.
WARI exposes them all when found in a reference.

## Reference types detected by the ArticleAnalyzer

We support detecting the following types. A reference cannot have multiple types.
We distinguish between two main types of references:

1) **named reference** - type of reference with only a name and no content e.g. '<ref name="INE"/>' (Unsupported
   beyond counting because we have not decided if they contain any value)
2) **content reference** - reference with any type of content
    1) **general reference** - subtype of content reference which is outside a <ref></ref> and usually found in
       sections called "Further reading" or "Bibliography"
       (unsupported but we want to support it, see
       https://github.com/internetarchive/wcdimportbot/labels/general%20reference)
       ![image](https://user-images.githubusercontent.com/68460690/208092363-ba4b5346-cad7-495e-8aff-1aa4f2f0161e.png)
    2) **footnote reference** - subtype of content reference which is inside a <ref> (supported partially, see below)

Example of a URL-template reference:
`<ref>Mueller Report, p12 {{url|http://example.com}} {{bare url inline}}</ref>`
This is a content reference -> a footnote reference -> a mixed reference with a URL template.

Example of an plain text reference:
`<ref>Muller Report, p12</ref>`
This is a footnote reference -> content reference -> Short citation reference aka naked named footnote.

# Endpoints

## Checking endpoints

### Check URL

the check-url endpoint accepts the following parameters:

* url (string, mandatory)
* refresh (boolean, optional)
* testing (boolean, optional)
* timeout (int, optional)
* debug (boolean, optional)

On error it returns 400.

It returns json similar to 
```
{
    "first_level_domain": "github.com",
    "fld_is_ip": false,
    "url": "https://github.com/internetarchive/iari/issues",
    "scheme": "https",
    "netloc": "github.com",
    "tld": "com",
    "malformed_url": false,
    "malformed_url_details": null,
    "archived_url": "",
    "wayback_machine_timestamp": "",
    "is_valid": true,
    "request_error": false,
    "request_error_details": "",
    "dns_record_found": true,
    "dns_no_answer": false,
    "dns_error": false,
    "status_code": 200,
    "testdeadlink_status_code": 200,
    "timeout": 2,
    "dns_error_details": "",
    "response_headers": {
        "Server": "GitHub.com",
        "Date": "Mon, 12 Jun 2023 12:00:28 GMT",
        "Content-Type": "text/html; charset=utf-8",
        "Vary": "X-PJAX, X-PJAX-Container, Turbo-Visit, Turbo-Frame, Accept-Encoding, Accept, X-Requested-With",
        "ETag": "W/\"03d14b06291209737bb700da5adf5968\"",
        "Cache-Control": "max-age=0, private, must-revalidate",
        "Strict-Transport-Security": "max-age=31536000; includeSubdomains; preload",
        "X-Frame-Options": "deny",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "0",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "Content-Security-Policy": "default-src 'none'; base-uri 'self'; block-all-mixed-content; child-src github.com/assets-cdn/worker/ gist.github.com/assets-cdn/worker/; connect-src 'self' uploads.github.com objects-origin.githubusercontent.com www.githubstatus.com collector.github.com raw.githubusercontent.com api.github.com github-cloud.s3.amazonaws.com github-production-repository-file-5c1aeb.s3.amazonaws.com github-production-upload-manifest-file-7fdce7.s3.amazonaws.com github-production-user-asset-6210df.s3.amazonaws.com cdn.optimizely.com logx.optimizely.com/v1/events *.actions.githubusercontent.com productionresultssa0.blob.core.windows.net/ productionresultssa1.blob.core.windows.net/ productionresultssa2.blob.core.windows.net/ productionresultssa3.blob.core.windows.net/ productionresultssa4.blob.core.windows.net/ wss://*.actions.githubusercontent.com github-production-repository-image-32fea6.s3.amazonaws.com github-production-release-asset-2e65be.s3.amazonaws.com insights.github.com wss://alive.github.com; font-src github.githubassets.com; form-action 'self' github.com gist.github.com objects-origin.githubusercontent.com; frame-ancestors 'none'; frame-src viewscreen.githubusercontent.com notebooks.githubusercontent.com; img-src 'self' data: github.githubassets.com media.githubusercontent.com camo.githubusercontent.com identicons.github.com avatars.githubusercontent.com github-cloud.s3.amazonaws.com objects.githubusercontent.com objects-origin.githubusercontent.com secured-user-images.githubusercontent.com/ user-images.githubusercontent.com/ private-user-images.githubusercontent.com opengraph.githubassets.com github-production-user-asset-6210df.s3.amazonaws.com customer-stories-feed.github.com spotlights-feed.github.com *.githubusercontent.com; manifest-src 'self'; media-src github.com user-images.githubusercontent.com/ secured-user-images.githubusercontent.com/ private-user-images.githubusercontent.com; script-src github.githubassets.com; style-src 'unsafe-inline' github.githubassets.com; worker-src github.com/assets-cdn/worker/ gist.github.com/assets-cdn/worker/",
        "Content-Encoding": "gzip",
        "Set-Cookie": "_gh_sess=Kt%2FbTAsPUlbQMLzfnhA6DaZ%2FrXJio0ITQdf7cs83MUTpiSwa0ALcco5FkiN3Gne6MBf%2Fzf001SNsFAAt1IXJVU9kFP5EOV1P1UZsps9JI2dyn9lAG0Zt%2FKocfikDwnYU03uuJAmDpI82mOt6L0ULDzxEm1hc0vCMRy72T8saF%2Ba8qoSFPJR296%2FjZVoqrg9cHzAnYr5uo0cj9dQL6pGfoDreWMMV41kG7S%2FbwvU5%2FTWkJnmYTK8XoioOtrVjnvQ%2Fw%2FNuMVh4dkEEeprnmfe8%2Bw%3D%3D--CpOcS3YATJ%2FQZh%2Fk--zuEd5QQlr0A8Pif7t41ywQ%3D%3D; Path=/; HttpOnly; Secure; SameSite=Lax, _octo=GH1.1.1345489649.1686571228; Path=/; Domain=github.com; Expires=Wed, 12 Jun 2024 12:00:28 GMT; Secure; SameSite=Lax, logged_in=no; Path=/; Domain=github.com; Expires=Wed, 12 Jun 2024 12:00:28 GMT; HttpOnly; Secure; SameSite=Lax",
        "Accept-Ranges": "bytes",
        "Transfer-Encoding": "chunked",
        "X-GitHub-Request-Id": "4C01:6326:116FFBB:1199F4E:648708DB"
    },
    "detected_language": "en",
    "detected_language_error": false,
    "detected_language_error_details": "",
    "timestamp": 1686564033,
    "isodate": "2023-06-12T12:00:33.941494",
    "id": "7e8230ce"
}
```

When the debug parameter is true the text from the resource is returned. 
This text is the basis for the language detection. 

#### Known limitations
You are very welcome to suggest improvements by opening an issue or sending a pull request. :)

#### Status codes
The status_code attribute is not as reliable as the testdeadlink_status_code.

Sometimes we get back a 403 because an intermediary like Cloudflare detected that we are not a person behind a browser
doing the request. We don't have any ways to detect these soft200s.

Also sometimes a server returns status code 200 but the content is an error page or any other content than what the
person asking for the information wants. These are called soft404s and we currently do not make any effort to detect
them.

#### Language detection
We need at least 200 characters to be able to reliably detect the language.

## Statistics

### article

the statistics/article endpoint accepts the following parameters:

* url (mandatory)
* refresh (optional)
* testing (optional)
* revision (int, optional) defaults to the most recent 

On error it returns 400. On timeout it returns 504 or 502
(this is a bug and should be reported).

It will return json similar to:

```
{
    "wari_id": "en.wikipedia.org.999263",
    "lang": "en",
    "page_id": 999263,
    "dehydrated_references": [
        {
            "id": "cfa8b438",
            "template_names": [],
            "type": "footnote",
            "footnote_subtype": "named",
            "flds": [],
            "urls": [],
            "titles": [],
            "section": "History"
        },
        {
            "id": "1db10c83",
            "template_names": [
                "citation"
            ],
            "type": "footnote",
            "footnote_subtype": "content",
            "flds": [
                "hydroretro.net"
            ],
            "urls": [
                "http://www.hydroretro.net/etudegh/sncase.pdf"
            ],
            "titles": [
                "Les r\u00e9alisations de la SNCASE"
            ],
            "section": "History"
        }
    ],
    "reference_statistics": {
        "named": 10,
        "footnote": 20,
        "content": 21,
        "general": 1
    },
    "served_from_cache": false,
    "site": "wikipedia.org",
    "timestamp": 1684217693,
    "isodate": "2023-05-16T08:14:53.932785",
    "timing": 0,
    "title": "SNCASO",
    "fld_counts": {
        "aviafrance.com": 3,
        "flightglobal.com": 2,
        "gouvernement.fr": 1,
        "jewishvirtuallibrary.org": 1,
        "hydroretro.net": 1,
        "google.com": 1
    },
    "urls": [
        "http://www.hydroretro.net/etudegh/sncase.pdf",
        "http://www.aviafrance.com/aviafrance1.php?ID_CONSTRUCTEUR=1145&ANNEE=0&ID_MISSION=0&CLE=CONSTRUCTEUR&MOTCLEF=",
        "https://www.gouvernement.fr/partage/9703-vol-historique-du-premier-avion-a-reaction-francais-le-so-6000-triton",
        "https://books.google.com/books?id=3y0DAAAAMBAJ&pg=PA128",
        "http://www.flightglobal.com/pdfarchive/view/1953/1953%20-%201657.html",
        "https://www.flightglobal.com/pdfarchive/view/1959/1959%20-%201053.html",
        "http://xplanes.free.fr/so4000/so4000-5.htm",
        "http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour",
        "http://www.aviafrance.com/constructeur.php?ID_CONSTRUCTEUR=1145",
        "http://www.aviafrance.com"
    ],
    "ores_score": {
        "prediction": "GA",
        "probability": {
            "B": 0.3001074961272599,
            "C": 0.2989581851995906,
            "FA": 0.03238239107761332,
            "GA": 0.33793161511968084,
            "Start": 0.0251506380008608,
            "Stub": 0.005469674474994447
        }
    }
}
```

#### Known limitations

* the general references parsing relies on 2 things:
    * a manually supplied list of sections to search using the 'regex' to the article and all endpoints. The list is
      case insensitive and should be delimited by the '|' character.
    * that every line with a general reference begins with a star character (*)

Any line that doesn't begin with a star is ignored.

### references

the statistics/references endpoint accepts the following parameters:

* wari_id (mandatory, str) (this is obtained from the article endpoint)
* all (optional, boolean) (default: false)
* offset (optional, int) (default: 0)
* chunk_size (optional, int) (default: 10)

On error it returns 400. If data is not found it returns 404.

It will return json similar to:

```
{
    "total": 31,
    "references": [
        {
            "id": "cfa8b438",
            "template_names": [],
            "wikitext": "<ref name = \"Hartmann1\" />",
            "type": "footnote",
            "footnote_subtype": "named",
            "flds": [],
            "urls": [],
            "templates": [],
            "titles": [],
            "section": "History",
            "served_from_cache": true
        },
    ]
}
```

#### Known limitations

None

### reference

the statistics/reference/id endpoint accepts the following parameters:

* id (mandatory) (this is unique for each reference and is obtained from the article or references endpoint)

On error it returns 400. If data is not found it returns 404.

It will return json similar to:

```
{
    "id": "cfa8b438",
    "template_names": [],
    "wikitext": "<ref name = \"Hartmann1\" />",
    "type": "footnote",
    "footnote_subtype": "named",
    "flds": [],
    "urls": [],
    "templates": [],
    "titles": [],
    "section": "History",
    "served_from_cache": true
}
```

#### Known limitations

None

### PDF

the statistics/pdf endpoint accepts the following parameters:

* url (mandatory)
* refresh (bool, optional, default false)
* testing (bool, optional, default false)
* timeout (int, optional, default 2 (seconds))
* debug (bool, optional) Note: you have to set refresh=true to be sure to get debug output.
  * html (bool, optional, default false)
  * xml (bool, optional, default false)
  * json_ (bool, optional, default false)
  * blocks (bool, optional, default false)

On error it returns 404 or 415. The first is when we could not find/fetch the url
and the second is when it is not a valid PDF.

If not given debug=true it will return json similar this

```
{
    "words_mean": 660,
    "words_max": 836,
    "words_min": 474,
    "annotation_links": [
        {
            "url": "http://arxiv.org/abs/2210.02667v1",
            "page": 0
        },...
    ],
    "links_from_original_text": [
        {
            "url": "https://www.un.org/en/about-us/universal-declaration-of-human-rights",
            "page": 1
        },
    ],
    "links_from_text_without_linebreaks": [
        {
            "url": "https://www.un.org/en/about-us/universal-declaration-of-human-rights3https://www.ohchr.org/en/issues/pages/whatarehumanrights.aspx4Legal",
            "page": 1
        },
    ],
    "links_from_text_without_spaces": [
        {
            "url": "https://www.un.org/en/about-us/universal-declaration-of-human-rights",
            "page": 1
        },
    ],
    "url": "https://arxiv.org/pdf/2210.02667.pdf",
    "timeout": 2,
    "pages_total": 17,
    "detected_language": "en",
    "detected_language_error": false,
    "detected_language_error_details": "",
    "characters": 74196,
    "timestamp": 1686055925,
    "isodate": "2023-06-06T14:52:05.228754",
    "id": "639dc1df"
}
```

Using the debug and refresh parameter, all the text before and after cleaning is exposed as well as the link-annotations
before url extraction. Using the 4 additional parameters you can get the corresponding output from PyMuPDF for further debugging.

Example debug expressions:
  
To show block debug output:
```
https://archive.org/services/context/iari/v2/statistics/pdf?url=https://ia601600.us.archive.org/31/items/Book_URLs/DeSantis.pdf&refresh=true&debug=true&blocks=true
```
To show html debug output:
```
https://archive.org/services/context/iari/v2/statistics/pdf?url=https://ia601600.us.archive.org/31/items/Book_URLs/DeSantis.pdf&refresh=true&debug=true&html=true
```
*Note: Setting debug=true parameter without refresh=true will often not yield any debug output since we don't have it
stored in the cache.*

*Warning: The debug outputs can generate very large output up to hundreds of MB 
so use with care or from the command line to avoid crashing your browser*  

This output permits the data consumer to count number of links per page, which links or domains appear most, number of
characters in the pdf and using the debug outputs you can investigate why the API could not find the links correctly.

#### Known limitations

The extraction of URLs from unstructured text in any random PDF is a
difficult thing to do reliably. This is because
PDF is not a structured data format with clear boundaries between different type of information.

We currently use PyMuPDF to extract all the text as it appears on the page. 
We clean the text in various ways to get the links out via a regex. 
This approach results in some links containing information that was part of the
text after the link ended but we have yet to find a way to reliably determine 
the end boundary of links.

We are currently investigating if using the html output of PyMuPdf or 
using advanced Machine Learning could improve the output.

You are very welcome to suggest improvements by opening an issue or sending a pull request. :)

### XHTML

the statistics/pdf endpoint accepts the following parameters:

* url (mandatory)
* refresh (optional)
* testing (optional)

On error it returns 400.

It will return json similar to:

```
{
    "links": [
        {
            "context": "<a accesskey=\"t\" href=\"http://www.hut.fi/u/hsivonen/test/xhtml-suite/\" title=\"The main page of this test suite\">This is a link to the <acronym title=\"Extensible HyperText Markup Language\">XHTML</acronym> test suite table of contents.</a>",
            "parent": "<p><a accesskey=\"t\" href=\"http://www.hut.fi/u/hsivonen/test/xhtml-suite/\" title=\"The main page of this test suite\">This is a link to the <acronym title=\"Extensible HyperText Markup Language\">XHTML</acronym> test suite table of contents.</a> The link contain inline markup (<code>&lt;acronym&gt;</code>), has a title and an accesskey \u2018t\u2019.</p>",
            "title": "The main page of this test suite",
            "href": "http://www.hut.fi/u/hsivonen/test/xhtml-suite/"
        },
        {
            "context": "<a href=\"base-target\">This is a relative link.</a>",
            "parent": "<p><a href=\"base-target\">This is a relative link.</a> If the link points to http://www.hut.fi/u/hsivonen/test/base-test/base-target, the user agent supports <code>&lt;base/&gt;</code>. if it points to http://www.hut.fi/u/hsivonen/test/xhtml-suite/base-target, the user agent has failed the test.</p>",
            "title": "",
            "href": "base-target"
        }
    ],
    "links_total": 2,
    "timestamp": 1682497512,
    "isodate": "2023-04-26T10:25:12.798840",
    "id": "fc5aa88d",
    "refreshed_now": false
}
```

#### Known limitations

None

# Installation

Clone the git repo:

`$ git clone https://github.com/internetarchive/iari.git && cd iari`

We recommend checking out the latest release before proceeding.

## Requirements

* python pip
* python gunicorn
* python poetry

## Setup

We use pip and poetry to set everything up.

`$ pip install poetry gunicorn && poetry install`

### Virtual environment
Setup:

`$ python3 -m venv venv`

Enter in (in a Linux/Mac terminal):

`$ source venv/bin/activate`

### JSON directories
Lastly setup the directories for the json cache files

`$ ./setup_json_directories.sh`

## Run

Run these commands in different shells or in GNU screen. 

Before running them please make sure you have activated the virtual environment first, see above.

### GNU screen
Start GNU screen (if you want to have a persisting session)

`$ screen -D -RR`

### Debug mode

Run it with
`$ ./run-debug-api.sh`

Test it in another Screen window or local terminal with
`$ curl -i "localhost:5000/v2/statistics/article?regex=external%20links&url=https://en.wikipedia.org/wiki/Test"`

### Production mode

Run it with
`$ ./run-api.sh`

Test it in another Screen window or local terminal with
`$ curl -i "localhost:8000/v2/statistics/article?regex=external%20links&url=https://en.wikipedia.org/wiki/Test"`

# PyCharm specific recommendations
## Venv activation
Make sure this setting is checked.
https://www.google.com/search?client=firefox-b-d&q=make+pycharm+automatically+enter+the+venv

# Deployed instances

See [KNOWN_DEPLOYED_INSTANCES.md](KNOWN_DEPLOYED_INSTANCES.md)

# Diagrams

## IARI

### Components

![image](diagrams/components.png)

# History of this repo

* version 1.0.0 a proof of concept import tool based on WikidataIntegrator (by James Hare)
* version 2.0.0+ a scalable ETL-framework with an API and capability of reading EventStreams (by Dennis Priskorn)
* version 3.0.0+ WARI, a host of API endpoints that returns statistics
  about a Wikipedia article and its references. (by Dennis Priskorn)
* version 4.0.0+ IARI, a host of API endpoints that returns statistics
  about both Wikipedia articles and its references and can extract links from any PDF or XHTML page. (by Dennis Priskor

# License

This project is licensed under GPLv3+. Copyright Dennis Priskorn 2022
The diagram PNG files are CC0.

# Further reading and installation/setup

See the [development notes](DEVELOPMENT_NOTES.md)
