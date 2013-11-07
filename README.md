# What
A router monitor used to keep track of upload/download bytes on a router.

# How
Clone this repository.

Use pip to install required packages

$ pip install -r requirements.pip

Make a copy of config.yaml.example to config.yaml
Modify config.yaml to suit your router values

## Monitor Router
Use crontab to run check.py

Sample crontab

*/5 * * * * cd router-monitor/ && ./check.py 2>&1 > ./run.log

Runs check.py every 5 minutes

## Run server
Run the server with

$ python server.py

## View usage

Open the server in a browser

http://localhost:8080/
