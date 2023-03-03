This directory contains the pydantic models related to the API 
that determine the patron facing json output.

The logic that analyzes an article only based on the wikitext is in
src/models/wikimedia/wikipedia/analyzer.py

The logic that does checking of identifiers is in src/models/checking

The purpose of separation is so that we at a later stage
can run the analysis and checking and output based on 
Wikipedia dump files and write the results to disk or a database.

In version 2 we adopted dehydrated references inspired by the OpenAlex API

We also split up into 5 endpoints:
* article
* reference
* references
* check-url
* check-doi

The references endpoint is limited to 100 dehydrated references and honors and offset.
To get the full reference use the reference endpoint. 

The reference endpoint returns all data we have.

The check-* endpoints lookup the identifier/URL in question and return data.
Check-url has an optional timeout= parameter which defaults to 2s

The purpose of this V2 was to 
* simplify
* make it faster by not doing the checking unless asked to
* make it possible for frontend developers to get data in a flash and 
query the checking endpoints asynchronously
* offload almost all counting and classification to the frontend developers