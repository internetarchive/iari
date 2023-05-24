# Known deployed instances of IARI
## Internet Archive
* Production (http, ip adress): http://18.217.22.248/
* Production: (proxied to add https and domain): https://archive.org/services/context/wari/
* Development: None

### Endpoint example urls for the production endpoint
The article/all/check-url/check-doi endpoints all return cached responses if you don’t add the refresh=true parameter.
The references and reference endpoints always return cached data.
Patron facing https proxy:
endpoint …/statistics/article
The article endpoint returns a high-level view of an article including all dehydrated references, overview of the type and subtypes of references found, all urls, etc.  A dehydrated reference is a reference without the templates and wikitext.
https://archive.org/services/context/wari/v2/statistics/article?url=https://en.wikipedia.org/wiki/Easter_Island&refresh=true/false&regex=bibliography|further reading|works cited|sources|external links

endpoint …/statistics/reference
The reference endpoint serves all details of a particular reference including all templates.
https://archive.org/services/context/wari/v2/statistics/reference/b64ae445

endpoint …/statistics/references
The references endpoint serves references either all at a time or in increments using offset (default = 0) and chunk_size (default = 10).
https://archive.org/services/context/wari/v2/statistics/references?wari_id=en.wikipedia.org.53418&all=true&offset=0&chunk_size=10

endpoint …/check-url
The check-url endpoint checks various parts of the url and looks it up and returns information about its HTTP status code
https://archive.org/services/context/wari/v2/check-url?url=https%3A%2F%2Fwww.easterisland.travel&timeout=3&refresh=true

endpoint …/check-doi
The check-doi endpoint looks up the DOI in 4 different sources (openalex, wikidata, fatcat and internet archive scholar) and tries to determine whether it has been retracted in openalex or wikidata.
https://archive.org/services/context/wari/v2/check-doi?doi=10.1136%2FGUT.52.12.1678&timeout=3&refresh=true

endpoint …/statistics/all
The all endpoint serves all data for a given article utilizing the other endpoints described above. In the case of many DOIs it will possibly return megabytes of data because it includes the full responses from 4 endpoints (which weigh about 200 kb per DOI).
https://archive.org/services/context/wari/v2/statistics/all?url=https://en.wikipedia.org/wiki/Easter_Island&refresh=true/false&regex=bibliography|further reading|works cited|sources|external links
