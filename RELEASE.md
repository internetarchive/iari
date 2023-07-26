# Deploy
* stop current docker container
* pull latest build
* setup config.py
```
cp config_sample.py config.py
```
* build docker image
```
docker image build -t iari . 
```
* start docker container (using port 5042 for testing)
```
docker container run --rm -it -p 5042:5000 -e "TESTDEADLINK_KEY=################################" iari ./app_run.py
```
to test (on local machine), try:
```
curl -i "localhost:5042/v2/check-url?refresh=true&url=https://www.smithsonianmag.com/travel/the-mystery-of-easter-island-151285298/"
# on aws server
http://47.208.158.224:5042/v2/check-url?refresh=true&url=https://www.smithsonianmag.com/travel/the-mystery-of-easter-island-151285298/
```
# Release
* Create new branch and PR
* Run PyCharm code inspection
* Run all tests and update the coverage
* Run `$ pre-commit run -all`
* Bump the version with `$ poetry version 3.0.0-alpha1` or `poetry patch`
* Run `$ poetry update`
[//]: # (* Export requirements `$ poetry export -o requirements.txt`)
* Commit changes and push
* When CI is successful merge the PR
* Create release in Github
* Publish to pypi `$ poetry publish --build`
