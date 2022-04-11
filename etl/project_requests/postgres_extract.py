movies_select = """
            SELECT film_work.id,
            film_work.rating AS imdb_rating,
            JSON_AGG(DISTINCT jsonb_build_object('id', genre.id, 'name', genre.name)) as genre,
            film_work.title,
            film_work.description,
            ARRAY_AGG(DISTINCT person.full_name)
            FILTER(WHERE person_film_work.role = 'director') AS director,
            ARRAY_AGG(DISTINCT person.full_name)
            FILTER(WHERE person_film_work.role = 'actor') AS actors_names,
            ARRAY_AGG(DISTINCT person.full_name)
            FILTER(WHERE person_film_work.role = 'writer') AS writers_names,
            JSON_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
            FILTER(WHERE person_film_work.role = 'actor') AS actors,
            JSON_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
            FILTER(WHERE person_film_work.role = 'writer') AS writers,
            JSON_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
            FILTER(WHERE person_film_work.role = 'director') AS directors
            FROM film_work
            LEFT OUTER JOIN genre_film_work ON (film_work.id = genre_film_work.film_work_id)
            LEFT OUTER JOIN genre ON (genre_film_work.genre_id = genre.id)
            LEFT OUTER JOIN person_film_work ON (film_work.id = person_film_work.film_work_id)
            LEFT OUTER JOIN person ON (person_film_work.person_id = person.id)
            GROUP BY film_work.id, film_work.title, film_work.description, film_work.rating
"""

genre_select = "SELECT json_build_object('id', id, 'name', name) FROM genre"
person_select = """
            SELECT person.id,
            person.full_name,
            ARRAY_AGG(DISTINCT person_film_work.role) AS role,
            ARRAY_AGG(DISTINCT person_film_work.film_work_id) AS film_ids
            FROM person
            LEFT OUTER JOIN person_film_work ON (person.id = person_film_work.person_id)
            GROUP BY person.id;
"""
