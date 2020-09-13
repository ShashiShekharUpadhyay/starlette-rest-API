from database.models import Movie, Genre
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from utils.exceptions import *
import pickle


class DatabaseServicer:
    """
    Base class for handling ORM session
    """
    def __init__(self, CONF, redis=None):
        self.CONF = CONF
        self.session = CONF.DB()
        self.redis = redis

    def get(self, param):
        """
        This method queries the 'movie' database and return a serialized response
        :param param: dict_item consisting of the query parameters
        :return: list of movie records
        """
        try:
            if len(param) > 0:
                key = list(param)[0][0]
                filters = {key: list(param)[0][1]}
                if key == 'genre':
                    results = self.session.query(Genre).filter(Genre.name == filters['genre']).first().movie_genres
                else:
                    results = self.session.query(Movie).filter_by(**filters).all()
                if results is None:
                    raise NoResultFound
            else:
                results = self.session.query(Movie).all()
            return [i.serialize for i in results]
        except NoResultFound:
            return ReadGetError(param)
        except Exception as e:
            self.CONF.Logger.info(e)
            raise ReadError
        finally:
            self.session.close()

    def delete(self, key: int):
        """
        This method deletes a record "movie" table based on the input id
        :param key: movie.id of the record to be deleted
        :return: Boolean
        """
        try:
            query = self.session.query(Movie).filter(Movie.id == key).first()
            if query is None:
                raise NoResultFound
            self.session.delete(query)
            self.session.commit()
            return True
        except NoResultFound:
            raise DeleteNoResultFoundError(key)
        except Exception as e:
            self.CONF.Logger.info(e)
            self.session.rollback()
            raise DeleteError
        finally:
            self.session.close()

    def add_genre(self, movie, genre_list):
        """
        This method appends genre to "movie" and handles integrity error
        :param movie: SqlAlchemy object
        :param genre_list: list of the genres to be appended
        :return:
        """
        for genre in genre_list:
            name = genre.strip()
            redis_obj = self.redis.get(name)
            if not redis_obj:
                genre = Genre(name=name)
                movie.genre.append(genre)
                self.session.flush()
                self.redis.set(name, pickle.dumps(genre))
            else:
                genre = pickle.loads(redis_obj)
                movie.genre.append(genre)
                self.session.flush()
        return movie

    def insert(self, fields: dict):
        """
        This method inserts a movie object in the database
        :param fields: dictionary containing fields to be added
        """
        try:
            payload = {'name': fields.get('name'), 'director': fields.get('director'),
                       'imdb_score': fields.get('imdb_score'), 'popularity': fields.get('popularity')}
            movie = Movie(**payload)
            self.session.add(movie)
            self.session.flush()
            genre_list = fields.get('genre')
            if genre_list:
                self.add_genre(movie, genre_list)
            self.session.commit()
        except Exception as e:
            self.CONF.Logger.error(e)
            self.session.rollback()
            raise AddError()
        finally:
            self.session.close()

    def update(self, param: dict):
        """
        This method updated an existing movie record
        :param param: dictionary containing the fields to be updated
        """
        try:
            query = self.session.query(Movie).filter(Movie.id == param['id'])
            genre_list = []
            if param.get('genre'):
                result = query.first()
                old_genres = result.serialize['genre']
                genre_list = param.get('genre')
                del param['genre']
                genre_list = list(list(set(old_genres)-set(genre_list)) + list(set(genre_list)-set(old_genres)))
            self.add_genre(query.first(), genre_list)
            del param['id']
            query.update(values=param)
            self.session.commit()
        except NoResultFound:
            self.session.rollback()
            raise UpdateNoResultFoundError(param['id'])
        except IntegrityError:
            pass
        except Exception as e:
            self.CONF.Logger.error(e)
            raise UpdateError
        finally:
            self.session.close()
