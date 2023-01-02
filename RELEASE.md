# Release
* Create new branch and PR
* Run PyCharm code inspection
* Run all tests
* Run `$ pre-commit run -all`
* Bump the version with `$ poetry version 3.0.0-alpha1` or `poetry patch`
* Run `$ poetry update`
[//]: # (* Export requirements `$ poetry export -o requirements.txt`)
* Commit changes and push
* When CI is successful merge the PR
* Create release in Github
* Publish to pypi `$ poetry publish --build`