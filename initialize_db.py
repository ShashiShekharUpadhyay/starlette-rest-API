import os
import json
from database.models import Movie, Genre, User, Base
from config import Cfg, constants
from sqlalchemy.exc import IntegrityError


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
                session.begin_nested()
                try:
                    genre = Genre(name=name)
                    movie.genre.append(genre)
                    session.add(movie)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    genre = session.query(Genre).filter(Genre.name == name).first()
                    movie.genre.append(genre)
                    session.add(movie)
                    session.commit()
        session.close()


def add_user(session):
    admins = ['shekhar', 'gaurang', 'sayali', 'ridha']
    for admin in admins:
        add = User(username=admin, is_admin=1)
        session.add(add)
    session.commit()


if __name__ == "__main__":
    CONF = Cfg(os.environ.get(constants.STAGE))
    Base.metadata.create_all(CONF.engine)
    base_path = dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{base_path}/database/imdb.json"
    populate_movies(file_path, CONF.DB())
    add_user(CONF.DB())
