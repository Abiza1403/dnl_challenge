# DNL Coding challenge

## Installation

A Docker Compose file has been provided for the project. The project can be cloned and run by using the below command,

```
docker-compose up -d --build
```

Two docker containers are created.

### challengednl_app container
Scrapes the data from the static website - https://www.urparts.com/index.cfm/page/catalogue.
Scraping takes about 20 minutes in total and loads a SQLite database 'catalogue.db'.

### challengednl_api container
Fast API app which retrieves data from the loaded 'catalogue.db'.
Can be accessed using:

```
localhost:8001
```
### Swagger UI
Get requests have been implemented in Swagger UI.
Can be accessed by pasing query parameters in:

```
localhost:8001/docs
```
