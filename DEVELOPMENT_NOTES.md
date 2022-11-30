# Developer notes

## Setting up the architecture locally
Install docker-compose and run

`sudo docker pull leobuskin/ssdb-docker`

Run these commands in different shells

`$ sudo docker compose up`
`$ ./run-worker.sh`
`$ ./run-ssdb.sh`
`$ ./run-api.sh`

and add a job via the API e.g.

`$ curl -i "localhost:8000/v1/add-job?lang=en&site=wikipedia&title=Test"`

which add a job for the article Test

## Architecture design
Version 2.1.0+ of the bot is using a stream based architecture
to distribute workloads efficiently and scale horizontally.

Decisions and principles guiding the design:
* The KISS-principle
* The IASandboxWikibase.cloud is the default Wikibase used. 
* Test coverage >90% is desired
* CI integration is desired (Currently we lack SSDB in 
Github Actions so that does not work)
* One class one concern ([separation of concerns](https://www.wikidata.org/wiki/Q2465506))
* Docker compose is used to bring up most of the architecture
* An updated diagram of all classes is desirable to get an overview
* An updated diagram of the workflow is desirable to get an overview

## Tests
### Coverage
Run
`python -m coverage run -m unittest && python -m coverage report`
### Find slow tests
Run 
`python -m pytest --durations=10`

[//]: # (# Class diagram)