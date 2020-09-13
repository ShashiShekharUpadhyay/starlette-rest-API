import os
import json
from database.models import Movie, Genre, Base
from config import Cfg, constants
import redis
import pickle

r = redis.from_url(os.environ['REDIS_URL'])


def populate_movies(file_path, session):
    """
    Populates the movies and genres tables
    :param file_path: path of the file
    :param session: ORM session
    :return:
    """
    with open(file_path, 'r') as f:
        raw_data = f.read()
        data = json.loads(raw_data)
        payload = {}
        for fields in data:
            payload['name'] = fields.get('name')
            payload['director'] = fields.get('director')
            payload['imdb_score'] = fields.get('imdb_score')
            payload['popularity'] = fields.get('99popularity')
            movie = Movie(**payload)
            session.add(movie)
            session.commit()
            genre_list = fields.get('genre')
            for genre in genre_list:
                name = genre.strip()
                redis_obj = r.get(name)
                if not redis_obj:
                    genre = Genre(name=name)
                    movie.genre.append(genre)
                    session.commit()
                    r.set(name, pickle.dumps(genre))
                else:
                    genre = pickle.loads(redis_obj)
                    movie.genre.append(genre)
                    session.commit()
                session.commit()
        session.close()


if __name__ == "__main__":
    r.flushdb()
    CONF = Cfg(os.environ.get(constants.STAGE))
    Base.metadata.create_all(CONF.engine)
    base_path = dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{base_path}/database/imdb.json"
    populate_movies(file_path, CONF.DB())
    r.flushdb()
