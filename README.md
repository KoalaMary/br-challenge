# Exponea Software Engineer assignment
HTTP server in Python which serves one endpoint `/api/smart`. 

It returns result of request to Exponea Testing HTTP Server.

## Installation
To install the dependencies run this command
```
pip install -r requirements.txt
```
## How to run the app
```
cd app
python -m flask run
```

## How to run the app via Docker
```
docker build -t flask_docker app
docker run -p 5000:5000 flask_docker
```