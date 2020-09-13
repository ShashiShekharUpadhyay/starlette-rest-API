from sqlalchemy import String, Column, Numeric, ForeignKey, MetaData, Table, Integer
from sqlalchemy.dialects.mysql.types import INTEGER, TINYINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData()

Base = declarative_base()

"""
Association Table for Many-To-Many Relationship
"""
MovieGenre = Table('movie_genre',
                   Base.metadata,
                   Column('movie_id', Integer, ForeignKey('movie.id'), primary_key=True),
                   Column('genre_id', Integer, ForeignKey('genre.id'), primary_key=True))


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=255), nullable=True)
    imdb_score = Column(Numeric(2, 1), nullable=True)
    popularity = Column(Numeric(3, 1), nullable=True)
    director = Column(String(length=255), nullable=True)
    genre = relationship('Genre', secondary=MovieGenre, backref=backref('movie_genres'), lazy='dynamic')

    @property
    def serialize(self):
        """
        :return: Formatted response dictionary
        """
        response = {'id': self.id}
        if self.name:
            response['name'] = self.name
        if self.imdb_score:
            response['imdb_score'] = float(self.imdb_score)
        if self.popularity:
            response['popularity'] = float(self.popularity)
        if self.director:
            response['director'] = self.director
        if self.genre:
            response['genre'] = [c.serialize for c in self.genre]
        return response


class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=100), primary_key=True, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    @property
    def serialize(self):
        """
        :return: Formatted response dictionary
        """
        if self.name:
            return self.name


class User(Base):
    __tablename__ = 'user'
    id = Column(INTEGER(20), primary_key=True, autoincrement=True)
    username = Column(String(length=255), nullable=True, unique=True)
    is_admin = Column(TINYINT(display_width=1), default=0)


