from sqlalchemy import Table, Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


film_genre_table = Table('film_genre', Base.metadata,
    Column('film_id', Integer, ForeignKey('films.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)


class Film(Base):
    __tablename__ = 'films'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    cover_url = Column(String)
    kp_rate = Column(Float)
    imdb_rate = Column(Float)
    duration = Column(Integer)
    country = Column(String)
    year = Column(Integer)
    # genre_id = Column(Integer, ForeignKey('genres.id'))
    genres = relationship('Genre', secondary=film_genre_table)

    def __unicode__(self):
        return u'<Film: {name}>'.format(name=self.name)


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    films = relationship('Film', secondary=film_genre_table)

    def __unicode__(self):
        return u'<Genre: {name}>'.format(name=self.name)


class Seanse(Base):
    __tablename__ = 'seanses'
    __table_args__ = (UniqueConstraint('beginning_at', 'finishing_at', 'film_id', 'cinema'),)

    id = Column(Integer, primary_key=True)
    beginning_at = Column(DateTime, nullable=False)
    finishing_at = Column(DateTime, nullable=False)
    film_id = Column(Integer, ForeignKey('films.id'))
    film = relationship('Film', backref='seanses')
    cinema = Column(String)

    def __unicode__(self):
        return u'<Seanse: {film} at {cinema} from {frm} to {to}>'.format(
            film=self.film.name, cinema=self.cinema,
            frm=self.beginning_at, to=self.finishing_at
        )
