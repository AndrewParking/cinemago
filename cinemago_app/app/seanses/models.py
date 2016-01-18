from sqlalchemy.schema import UniqueConstraint
from .. import db


class Film(db.Model):
    __tablename__ = 'films'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String)
    kp_rate = db.Column(db.Float)
    imdb_rate = db.Column(db.Float)
    duration = db.Column(db.Integer)
    country = db.Column(db.String)
    year = db.Column(db.Integer)
    # genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))

    def __repr__(self):
        return '<Film: {name}>'.format(name=self.name)

    def to_native(self):
        return dict(
            name=self.name,
            description=self.description,
            cover_url=self.cover_url,
            kp_rate=self.kp_rate,
            imdb_rate=self.imdb_rate,
            duration=self.duration,
            country=self.country,
            year=self.year,
            genres=[genre.name for genre in self.genres]
        )

    def update_from_form_data(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
        db.session.add(self)
        db.session.commit()



film_genre_table = db.Table('film_genre',
    db.Column('film_id', db.Integer, db.ForeignKey('films.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'))
)


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    films = db.relationship('Film', secondary=film_genre_table,
        backref='genres', lazy='dynamic')

    def __repr__(self):
        return '<Genre: {name}>'.format(name=self.name)

    def to_native(self):
        return dict(
            id=self.id,
            name=self.name
        )

    def update_from_form_data(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
        db.session.add(self)
        db.session.commit()


class Seanse(db.Model):
    __tablename__ = 'seanses'
    __table_args__ = (UniqueConstraint('beginning_at', 'finishing_at', 'film_id', 'cinema'),)

    id = db.Column(db.Integer, primary_key=True)
    beginning_at = db.Column(db.DateTime, nullable=False)
    finishing_at = db.Column(db.DateTime, nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'))
    film = db.relationship('Film', backref='seanses')
    cinema = db.Column(db.String)

    def __repr__(self):
        return '<Seanse: {film} at {cinema} from {frm} to {to}>'.format(
            film=self.film.name, cinema=self.cinema,
            frm=self.beginning_at, to=self.finishing_at
        )
