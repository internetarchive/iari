# Developer notes

## Installation
Clone the git repo:

`$ git clone https://github.com/internetarchive/wcdimportbot.git`
`$ cd wcdimportbot`

We recommend checking out the latest release before proceeding.

## Setup
We use pip and poetry to set everything up.

`$ pip install poetry`
`$ poetry install `

[Generate a botpassword](https://wikicitations.wiki.opencura.com/w/index.php?title=Special:UserLogin&returnto=Special%3ABotPasswords&returntoquery=&force=BotPasswords)

Copy config.py.sample -> config.py 
`$ cp config.py.sample config.py`
and 
enter your botpassword credentials. E.g. user: "test" and password: "q62noap7251t8o3nwgqov0c0h8gvqt20"
`$ nano config.py`

If you want to delete items from the Wikibase, ask an administrator of the Wikibase to become admin.

## Running the framework
We use docker-compose to run some parts of the framework. We would like to add an ingester and a couple of workers to docker-compose, but [this bug](https://github.com/internetarchive/wcdimportbot/issues/224) is currently preventing that.

Install docker-compose and run

`sudo docker pull leobuskin/ssdb-docker`

Run these commands in different shells or in GNU screen.

Start GNU screen (if you want to have a persisting session)
`$ screen -D -RR`

Start the cache database
`$ ./run-ssdb.sh`

Start docker
`$ sudo docker compose up`

Start the rest
`$ ./run-worker.sh`
`$ ./run-api.sh`

and add a job via the API e.g.

`$ curl -i "localhost:8000/v1/add-job?lang=en&site=wikipedia&title=Test"`

which add a job for the article Test

## CLI Usage examples

### Import one or more pages
The bot can import any Wikipedia article (in English Wikipedia)

`$ python wcdimportbot.py --import "title of article"` 

### Import range
The bot can import ranges of Wikipedia articles (in English Wikipedia) in the order A-Z

`$ python wcdimportbot.py --max-range 10` 

### Import range based on category
The bot can import ranges of Wikipedia articles (in English Wikipedia)

`$ python wcdimportbot.py --category "title of category"` 

### Help
Run `$ python wcdimportbot.py --help` to see a list of all supported commands

## Architecture design
### Graph generation architecture
WIP algorithm version 0:

Generation phase:
1. hash the article wikitext (article_wikitext_hash)
2. Parse the article Wikitext
3. generate the article_hash
4. generate the base item using WBI
5. Store the json data using the hash (in ssdb)
6. hash the wikitext of all the references found (reference_wikitext_hash)
7. generate the reference item if an identifier was found
8. Store the generated reference json in ssdb with the reference_hash as key
9. Store the reference wikitext using the reference_wikitext_hash as key in ssdb
10. keep a record of which articles has which raw reference hashes in ssdb with key=article_hash+"refs" as key and a list of reference_wikitext_hash as value if any
11. keep a record of hashed references for each article in ssdb with key=article_hash+reference_hash, value list of identifier hashes if any)

We intentionally do not generate website items, nor handle the non-hashable references in this first iteration. 

Upload phase:
1. Open a connection to Wikibase using WikibaseIntegrator.
2. Loop over all references and upload the json to Wikibase for each unique reference
3. store the resulting wcdqid in ssdb (key=reference_hash+"wcdqid" value=wcdqid)
4. loop over all articles and finish generating the item using unihash list and get the wcdqids for references from ssdb. 
   * Upload up to a max of 500 references on an article in one go, discard any above that.

Improvements for next iteration:
* add any surplus references using addclaim to avoid throwing a way good data.

### Stream based architecture (abandoned)
Version 2.1.0+ of the bot is using a stream based architecture
to distribute workloads efficiently and scale horizontally.

Decisions and principles guiding the design:
* The [KISS-principle](https://www.wikidata.org/wiki/Q131560)
* The [IASandboxWikibase.cloud](https://ia-sandbox.wikibase.cloud/) is the default Wikibase used. 
* Test coverage >90% is desired
* CI integration is desired (Currently we lack SSDB in 
Github Actions so that does not work)
* One class one concern ([separation of concerns](https://www.wikidata.org/wiki/Q2465506))
* Docker compose is used to bring up most of the architecture
* An updated diagram of all classes is desirable to get an overview
* An updated diagram of the workflow is desirable to get an overview

## Tests
### Coverage
We have a helper script which updates [TEST_COVERAGE.txt](TEST_COVERAGE.txt):
`./run-test-coverage.sh`

### Find slow tests
Run 
`python -m pytest --durations=10`

[//]: # (# Class diagram)