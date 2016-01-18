# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeanseItem(scrapy.Item):
    film_name = scrapy.Field()
    film_description = scrapy.Field()
    film_cover_url = scrapy.Field()
    film_kp_rate = scrapy.Field()
    film_imdb_rate = scrapy.Field()
    film_duration = scrapy.Field()
    film_country = scrapy.Field()
    film_year = scrapy.Field()
    genres_names = scrapy.Field()
    beginning_at = scrapy.Field()
    finishing_at = scrapy.Field()
    date = scrapy.Field()
    cinema = scrapy.Field()
    genre = scrapy.Field()
    film = scrapy.Field()
    genres = scrapy.Field()
