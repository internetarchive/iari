# Developer notes

## CLI Usage examples

## Architecture design ideas for future graph generation
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
