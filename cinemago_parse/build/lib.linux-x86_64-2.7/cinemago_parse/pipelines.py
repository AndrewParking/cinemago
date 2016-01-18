# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cinemago_parse.models import Film, Genre, Seanse

DBG = []

MONTHS = {
    u'янв': 1,
    u'фев': 2,
    u'мар': 3,
    u'апр': 4,
    u'май': 5,
    u'июн': 6,
    u'июл': 7,
    u'авг': 8,
    u'сен': 9,
    u'окт': 10,
    u'ноя': 11,
    u'дек': 12,
}

STRIP_TARGET_FIELDS = (
    'cinema',
    'film_name',
    'film_country',
    'film_description',
    'film_director',
)

# Base pipline class for working with database

class DBPipeline(object):

    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(db_url=crawler.settings['DATABASE_URI'])

    def open_spider(self, spider):
        self.Session = sessionmaker(bind=self.engine)


# Actual pipelines

class ProcessDateTimePipeline(object):

    def process_item(self, item, spider):
        if item.get('film_duration') and item.get('date') and item.get('beginning_at'):
            s = item['film_duration']
            duration_int = int(s[0:s.find(' ')])
            duration = timedelta(minutes=duration_int)
            item['film_duration'] = duration_int
            month_index = item['date'].split(' ')[1][:3]
            month = MONTHS[month_index]
            day = int(item['date'].split(' ')[0])
            hours = int(item['beginning_at'].split(':')[0])
            minutes = int(item['beginning_at'].split(':')[1])
            item['beginning_at'] = datetime(year=datetime.utcnow().year,
                month=month, day=day, hour=hours, minute=minutes)
            item['finishing_at'] = item['beginning_at'] + duration
            return item
        raise DropItem


class ProcessRatesPipeline(object):

    def process_item(self, item, spider):
        if item.get('film_kp_rate'):
            item['film_kp_rate'] = float(item['film_kp_rate'].replace(',', '.'))
        if item.get('film_imdb_rate'):
            item['film_imdb_rate'] = float(item['film_imdb_rate'].replace(',', '.'))
        return item


class RemoveWhitespacePileline(object):

    def process_item(self, item, spider):
        for key in item.keys():
            if key in STRIP_TARGET_FIELDS:
                item[key] = item[key].strip()
        return item


class GenreToDBPipeline(DBPipeline):

    def process_item(self, item, spider):
        session = self.Session()
        if item.get('genres_names'):
            item['genres'] = []
            for name in item['genres_names']:
                genre = session.query(Genre).filter_by(name=name).first()
                if genre is None:
                    genre = Genre(name=name)
                    session.add(genre)
                    session.commit()
                item['genres'].append(genre)
            # genre = session.query(Genre).filter_by(name=item['genre_name']).first()
            # if genre is None:
            #     genre = Genre(name=item['genre_name'])
            #     session.add(genre)
            #     session.commit()
            # item['genre'] = genre
        session.close()
        return item


class FilmToDBPipeline(DBPipeline):

    def process_item(self, item, spider):
        session = self.Session()
        if item.get('film_name'):
            film = session.query(Film).filter_by(name=item['film_name']).first()
            if film is None:
                film = Film(
                    name=item['film_name'],
                    description=item.get('film_description'),
                    cover_url=item.get('film_cover_url'),
                    kp_rate=item.get('film_kp_rate'),
                    imdb_rate=item.get('film_imdb_rate'),
                    duration=item.get('film_duration'),
                    country=item.get('film_country'),
                    year=item.get('film_year')
                )
                if item.get('genres'):
                    for genre in item['genres']:
                        film.genres.append(genre)
                session.add(film)
                session.commit()
            item['film'] = film
        session.close()
        return item


class SeanseToDBPipeline(DBPipeline):

    def process_item(self, item, spider):
        # TODO: unique constraint for all fields together in order to avoid dubl
        session = self.Session()
        seanse = Seanse(
            beginning_at=item['beginning_at'],
            finishing_at=item['finishing_at'],
            film=item.get('film'),
            cinema=item.get('cinema')
        )
        session.add(seanse)
        session.commit()
        session.close()
        return item
