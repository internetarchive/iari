# Developer notes

## Setting up the architecture locally
Install docker, docker-compose and run

`sudo docker pull leobuskin/ssdb-docker`

Run these commands in different shells

`$ sudo docker compose up`
`$ ./run-worker.sh`
`$ ./run-ssdb.sh`

Now test the architecture by setting up wikicitations-api from
https://github.com/dpriskorn/wikicitations-api/

Start it with

`$ python app.py`
and add a job via the API e.g.

`$ curl -i "localhost:5000/v1/add-job?lang=en&site=wikipedia&title=Test"`

## Architecture design
Version 2 of the bot is using a stream based architecture
to distribute workloads efficiently and scale horizontally.

Decisions and principles guiding the design:
* The KISS-principle
* The IASandboxWikibase.cloud is the default Wikibase used. 
* Test coverage >90% is desired
* CI integration is desired (Currently we lack SSDB in 
Github Actions so that does not work)
* One class one concern (separation of concern)
* Docker compose is used to bring up most of the architecture
* An updated diagram of all classes is desireable to get an overview
* An updated diagram of the workflow is desireable to get an overview

## Test coverage
Run
`python -m coverage run -m unittest`
`python -m coverage report`

[//]: # (# Class diagram)

[//]: # (# Sequence diagram for import of one page)
