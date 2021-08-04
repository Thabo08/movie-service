[![workflow](https://github.com/Thabo08/movies/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/Thabo08/movies/actions/workflows/main.yml)

# Movie Service
Movie service is REST API that allows clients to search for movies of their favourite artists. The search functionality
applies the following filter based logic:

1. Search for all movies by the artist
2. Search for all movies by the artist by a specific genre
3. Search for all movies by the artist released in a specific year
4. Search for all movies by the artist released in a specific year and for a specific genre

The API is written in Python and uses the [Django](https://www.djangoproject.com/) web framework. When a request comes in,
the service makes an external call to the [iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)
to retrieve rich movie data about an artist. The data is then transformed to an internal domain model and then stored
in a cache (Memcached) before it is sent back to the client. Subsequent requests for movie data of the specific artist
will then be looked up in the cache, rather than making the external API call.

Movie data can change every 24 hours. As a result, no persistent storage is used as it would complicate the architecture
(remove persisted data every 24 hours?) and be of little benefit. Loss of data is also not detrimental in this case. The cache is then set to expire entries
every 24 hours. Caching allows for quick retrievals of entries that have already been cached.


### Installation
The movie service can be ran locally by following these steps:
#### Project checkout
```git
   ssh: git clone git@github.com:Thabo08/movie-service.git
   https: git clone https://github.com/Thabo08/movie-service.git
```

#### Installing dependencies
```shell
   cd movie-service
   pip install -r requirements.txt
```

#### Integration tests
```python
   python movies/manage.py test movies_api
```

#### Running the service
```docker
   docker compose up --build -d
```


### Usage
The service can be used in the following ways to perform different searches. The sample responses are provided for each
sample request. By default, the service runs on http://127.0.0.1:8000.

1. Search for all movies by the artist:
    ```
        GET /api/v1/movies?firstname=kevin&lastname=hart
   ```
   ```json
      {
       "kevin hart": [
        {
            "name": "The Secret Life of Pets",
            "release date": 2016,
            "genre": "Kids & Family"
        },
        {
            "name": "Central Intelligence",
            "release date": 2016,
            "genre": "Comedy"
        }
      ]
     }
   ```
2. Search for all movies by the artist by a specific genre:
    ```
        GET /api/v1/movies?firstname=kevin&lastname=hart&genre=comedy
   ```
   ```json
      {
       "kevin hart": [
        {
            "name": "Kevin Hart: Let Me Explain",
            "release date": 2013,
            "genre": "Comedy"
        },
        {
            "name": "Central Intelligence",
            "release date": 2016,
            "genre": "Comedy"
        }
      ]
     }
   ```
3. Search for all movies by the artist released in a specific year:
    ```
        GET /api/v1/movies?firstname=kevin&lastname=hart&releaseDate=2019
   ```
   ```json
      {
       "kevin hart": [
        {
            "name": "Jumanji: The Next Level",
            "release date": 2019,
            "genre": "Action & Adventure"
        },
        {
            "name": "The Secret Life of Pets 2",
            "release date": 2019,
            "genre": "Kids & Family"
        }
      ]
     }
   ```
4. Search for all movies by the artist released in a specific year and for a specific genre:
    ```
        GET /api/v1/movies?firstname=kevin&lastname=hart&releaseDate=2013&genre=comedy
   ```
   ```json
      {
       "kevin hart": [
        {
            "name": "Kevin Hart: Let Me Explain",
            "release date": 2013,
            "genre": "Comedy"
        },
        {
            "name": "Grudge Match",
            "release date": 2013,
            "genre": "Comedy"
        }
      ]
     }
   ```