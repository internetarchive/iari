This directory contains the pydantic models related to the API 
that determine the patron facing json output.

The logic that analyzes an article only based on the wikitext is in
src/models/wikimedia/wikipedia/analyzer.py

The logic that does checking of identifiers is in src/models/checking

The purpose of separation is so that we at a later stage
can run the analysis and checking and output based on 
Wikipedia dump files and write the results to disk or a database.