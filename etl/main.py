import os.path
import datetime
import elasticsearch
from utils import backoff
from config import config, dsl, logger
from etl import (CheckDataChange,
                 JSONCreate,
                 ImportToElastic,
                 PostgresExtract,
                 CreateIndex)
from project_requests import postgres_extract


@backoff()
def movies():
    if os.path.exists('./modify/movies.json'):
        try:
            now = datetime.datetime.now()
            time_to_check = now + datetime.timedelta(minutes=1)
            films_db_last_mod = CheckDataChange(dsl, 'movies').load_last_mod()

            if time_to_check.strftime("%Y-%m-%d %H:%M:%S") > films_db_last_mod:
                films_db = CheckDataChange(dsl, 'movies').check_change()
                films_json = JSONCreate(films_db, 'movies')
                films_json_dataclass = films_json.create_movies_dataclass_list()
                films_json.create_movies_data_to_elastic(films_json_dataclass)
                return es.bulk(
                    index='movies',
                    body=ImportToElastic(
                        'data/movies.json'
                    ).bulk_data_to_elastic()
                )

        except ValueError as error:
            logger.error(error)
    else:
        films_db = PostgresExtract(
            postgres_extract.movies_select,
            'movies', dsl).retrieve_data_from_postgres()

        films_index = CreateIndex(
            'index/movie_schema.json',
            'movies',
            config
        )
        films_index.create_index()

        films_json = JSONCreate(films_db, 'movies')
        films_json_dataclass = films_json.create_movies_dataclass_list()
        films_json.create_movies_data_to_elastic(films_json_dataclass)
        es.bulk(
            index='movies',
            body=ImportToElastic('data/movies.json').bulk_data_to_elastic()
        )


@backoff()
def genres():
    if os.path.exists('./modify/gernes.json'):
        try:
            now = datetime.datetime.now()
            time_to_check = now + datetime.timedelta(minutes=1)
            genres_db_last_mod = CheckDataChange(dsl, 'genres').load_last_mod()

            if time_to_check.strftime("%Y-%m-%d %H:%M:%S") > genres_db_last_mod:
                genre_db = CheckDataChange(dsl, 'genres').check_change()
                genres_json = JSONCreate(genre_db, 'genres')
                genres_json_dataclass = genres_json.create_genres_dataclass_list()
                genres_json.create_genres_data_to_elastic(genres_json_dataclass)
                return es.bulk(
                    index='genres',
                    body=ImportToElastic(
                        'data/genres.json'
                    ).bulk_data_to_elastic()
                )

        except ValueError as error:
            logger.error(error)
    else:
        genre_db = PostgresExtract(
            postgres_extract.genre_select,
            'genres',
            dsl
        ).retrieve_data_from_postgres()

        genre_index = CreateIndex(
            'index/genre_schema.json',
            'genres',
            config
        )
        genre_index.create_index()

        genres_json = JSONCreate(genre_db, 'genres')
        genres_json_dataclass = genres_json.create_genres_dataclass_list()
        genres_json.create_genres_data_to_elastic(genres_json_dataclass)
        return es.bulk(
            index='genres',
            body=ImportToElastic('data/genres.json').bulk_data_to_elastic()
        )


@backoff()
def persons():
    if os.path.exists('./modify/persons.json'):
        try:
            now = datetime.datetime.now()
            time_to_check = now + datetime.timedelta(minutes=1)
            persons_db_last_mod = CheckDataChange(
                dsl,
                'persons'
            ).load_last_mod()

            if time_to_check.strftime("%Y-%m-%d %H:%M:%S") > persons_db_last_mod:
                person_db = CheckDataChange(dsl, 'persons').check_change()
                persons_json = JSONCreate(person_db, 'persons')
                persons_json_dataclass = persons_json.create_persons_dataclass_list()
                persons_json.create_persons_data_to_elastic(
                    persons_json_dataclass
                )
                return es.bulk(
                    index='persons',
                    body=ImportToElastic(
                        'data/persons.json'
                    ).bulk_data_to_elastic()
                )

        except ValueError as error:
            logger.error(error)
    else:
        person_db = PostgresExtract(
            postgres_extract.person_select,
            'persons', dsl).retrieve_data_from_postgres()

        person_index = CreateIndex(
            'index/person_schema.json',
            'persons',
            config
        )
        person_index.create_index()

        persons_json = JSONCreate(person_db, 'persons')
        persons_json_dataclass = persons_json.create_persons_dataclass_list()
        persons_json.create_persons_data_to_elastic(persons_json_dataclass)
        return es.bulk(
            index='persons',
            body=ImportToElastic('data/persons.json').bulk_data_to_elastic()
        )


if __name__ == '__main__':
    if not os.path.exists('./data'):
        os.makedirs('./data')

    if not os.path.exists('./modify'):
        os.makedirs('./modify')

    es = elasticsearch.Elasticsearch([config], request_timeout=300)

    movies()
    genres()
    persons()
