# What is Wikibase?
Wikibase is a FLOSS graph database which enables users to store large
amounts of information and query them using [SPARQL](https://en.wikibooks.org/wiki/SPARQL).
Wikibase has been created by [Wikimedia Deutchland](https://www.wikimedia.de/) and is
maintained by them as of this writing.

# Why store the data about references in a graph database?
The advantages of having access to this data in a graph are many.
* [Globally unique and persistent identifiers](https://www.wikidata.org/wiki/Q115493815) (aka. GUPRI)
for as many references in Wikipedia as possible.
* Helping Wikipedians to improve the references, so they can be uniquely identified and can be
[_turned blue_](https://www.wikidata.org/wiki/Q115136754)
([video](https://commons.wikimedia.org/wiki/File:Let%E2%80%99s_Turn_all_the_References_Blue.webm))
* Overview and visualization of references across Wikipedia articles and language editions becomes possible.
* Overview of most cited websites in the world (see also [bestref.net](https://bestref.net/)
which is based on data extraction from the dump files)
* Insight into how many references have URLs, authors and other valuable information.
* Using SPARQL it becomes trivial for anyone to e.g. pinpoint pages with less trustworthy sources
* Using the data over time can help follow and understand changes in patterns of referencing.
* and more...

# Use cases
1. To support various queries of various citation types to learn various things about cited material.
E.g. number of citations per source or publication.
2. To be able to query to learn about how well citations are linked... to help us understand the gaps,
scale and scope of the Goal of Turn All References Blue.

# Estimated size
200+ million reference items (add source to research extracting references from Wikipedias).
100+ million website items (guesstimate).
[60 million wikipedia article](
https://en.wikipedia.org/wiki/Wikipedia:Size_of_Wikipedia#Comparisons_with_other_Wikipedias)
items. In total ~260 million items. For comparison
[Wikidata as of this writing have 100 million items](
https://grafana.wikimedia.org/d/000000489/wikidata-query-service?orgId=1&refresh=1m).

In total, we estimate we will have 15 triples per item which equals 15 bn triples in total.
For comparison,
[Wikidata as of this writing have 14.4 bn triples](
https://grafana.wikimedia.org/d/000000489/wikidata-query-service?orgId=1&refresh=1m).

