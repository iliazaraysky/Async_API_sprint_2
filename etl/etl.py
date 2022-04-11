import json
import datetime
import psycopg2
import elasticsearch
from dataclass import Movie, Genre, Person
from dotenv import load_dotenv
from config import logger
from project_requests import change_check


load_dotenv()


class ImportToElastic:
    def __init__(self, file):
        self.file = file

    def bulk_data_to_elastic(self):
        with open(self.file) as json_file:
            data = json.load(json_file)
            logger.info('Импорт данных в ES завершен')
            return data


class JSONCreate:
    def __init__(self, data_from_postgres, index_name):
        self.data_from_postgres = data_from_postgres
        self.index_name = index_name

    def create_movies_dataclass_list(self):
        body = []
        for row in self.data_from_postgres:
            data_template = Movie(
                id=row[0],
                imdb_rating=row[1],
                genre=row[2],
                title=row[3],
                description=row[4],
                director=row[5],
                actors_names=row[6],
                writers_names=row[7],
                actors=row[8],
                writers=row[9],
                directors=row[10]
            )
            body.append(data_template)
        return body

    def create_genres_dataclass_list(self):
        body = []
        for row in self.data_from_postgres:
            data_template = Genre(
                id=row[0]['id'],
                name=row[0]['name']
            )
            body.append(data_template)
        return body

    def create_genres_data_to_elastic(self, dataclass_list):
        with open(f'data/{self.index_name}.json', 'w') as f:
            body = []
            for row in dataclass_list:
                index_template = {"index": {"_index": "genres", "_id": str(row.id)}}
                data_template = {
                    "id": str(row.id),
                    "name": row.name
                }
                body.append(index_template)
                body.append(data_template)
            json.dump(body, f, indent=4)

    def create_movies_data_to_elastic(self, dataclass_list):
        with open(f'data/{self.index_name}.json', 'w') as f:
            body = []
            for row in dataclass_list:
                index_template = {"index": {"_index": "movies", "_id": str(row.id)}}
                data_template = {
                    "id": str(row.id),
                    "imdb_rating": row.imdb_rating,
                    "genre": row.genre,
                    "title": row.title,
                    "description": row.description,
                    "director": row.director,
                    "actors_names": row.actors_names,
                    "writers_names": row.writers_names,
                    "actors": row.actors,
                    "writers": row.writers,
                    "directors": row.directors
                }
                body.append(index_template)
                body.append(data_template)
            json.dump(body, f, indent=4)

    def create_persons_dataclass_list(self):
        body = []
        for row in self.data_from_postgres:
            film_ids = row[3].replace('{', '').replace('}', '').split(',')
            data_template = Person(
                id=row[0],
                full_name=row[1],
                role=row[2],
                film_ids=film_ids
            )
            body.append(data_template)
        return body

    def create_persons_data_to_elastic(self, dataclass_list):
        with open(f'data/{self.index_name}.json', 'w') as f:
            body = []
            for row in dataclass_list:
                index_template = {"index": {"_index": "persons", "_id": str(row.id)}}
                data_template = {
                    "id": str(row.id),
                    "full_name": row.full_name,
                    "role": row.role,
                    "film_ids": row.film_ids
                }
                body.append(index_template)
                body.append(data_template)
            json.dump(body, f, indent=4)


class CheckDataChange:
    def __init__(self, db_connection, index_name):
        self.db_connection = db_connection
        self.index_name = index_name

    def set_last_change_date(self, index_name: str):
        body = []
        with open(f'./modify/{index_name}.json', 'w') as f:
            now = datetime.datetime.now()
            data_template = {
                "last_modify": now.strftime("%Y-%m-%d %H:%M:%S")
            }
            body.append(data_template)
            json.dump(body, f, indent=4)
        f.close()

    def load_last_mod(self):
        try:
            with open(f'./modify/{self.index_name}.json', 'r') as f:
                data = json.load(f)
                return data[0]['last_modify']
        except FileNotFoundError as error:
            logger.error(error)

    def check_change(self):
        conn = psycopg2.connect(**self.db_connection)
        cursor = conn.cursor()
        last_mod = self.load_last_mod()
        try:
            cursor.execute(f"{change_check.check_data_change}" % last_mod)
            row = cursor.fetchall()
            self.set_last_change_date(self.index_name)
            return row
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            if conn is not None:
                conn.close()


class PostgresExtract:
    def __init__(self, query, index_name, db_connect):
        self.query = query
        self.db_connect = db_connect
        self.index_name = index_name

    def set_last_change_date(self, index_name: str):
        body = []
        with open(f'./modify/{index_name}.json', 'w') as f:
            now = datetime.datetime.now()
            data_template = {
                "last_modify": now.strftime("%Y-%m-%d %H:%M:%S")
            }
            body.append(data_template)
            json.dump(body, f, indent=4)
        f.close()

    def retrieve_data_from_postgres(self):
        conn = psycopg2.connect(**self.db_connect)
        cursor = conn.cursor()
        try:
            cursor.execute(f"{self.query}")
            row = cursor.fetchall()
            self.set_last_change_date(self.index_name)
            return row
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            if conn is not None:
                conn.close()


class CreateIndex:
    def __init__(self, path, index_name, es_connect_conf):
        self.path = path
        self.index_name = index_name
        self.es_connect_conf = es_connect_conf

    def create_index(self):
        with open(self.path, 'r') as file:
            data = file.read()
            es = elasticsearch.Elasticsearch([self.es_connect_conf], request_timeout=300)
            try:
                es.indices.create(index=self.index_name, body=data)
                logger.info(f'Создание {self.index_name} индекса завершено')
            except elasticsearch.exceptions.RequestError as ex:
                if ex.error == 'resource_already_exists_exception':
                    pass
                else:
                    raise ex
