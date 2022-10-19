# Setting up the architecture locally
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

# Class diagram
# Sequence diagram for import of one page
