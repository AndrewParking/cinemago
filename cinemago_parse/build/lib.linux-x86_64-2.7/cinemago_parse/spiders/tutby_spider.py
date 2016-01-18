import scrapy
from cinemago_parse.items import SeanseItem


class TutBySpider(scrapy.Spider):
    name = 'tutby'
    allowed_hosts = ['afisha.tut.by']
    start_urls = ['http://afisha.tut.by/film/']

    def parse(self, response):
        for sel in response.css('ul.list_afisha.col-5 .lists__li'):
            link = sel.css('a.name::attr(href)').extract()[0]
            yield scrapy.Request(link, callback=self.parse_film)

    def parse_film(self, response):
        temp = {}
        try:
            temp['film_name'] = response.css('.post .title::text').extract()[0]
            temp['film_description'] = response.css('.col-i .post').extract()[0]
            temp['film_cover_url'] = response.css('.post_wrapper .image_wrapper img::attr(src)').extract()[0]
            temp['film_kp_rate'] = response.css('.post .movie_rating .IMDb b:last-of-type::text').extract()[0]
            temp['film_imdb_rate'] = response.css('.post .movie_rating .IMDb b:first-of-type::text').extract()[0]
            temp['film_duration'] = response.css('.post .movie_info .duration::text').extract()[0]
            temp['film_country'] = response.css('.post .movie_info .author::text').extract()[0]
            temp['film_year'] = response.css('.post .movie_info .year::text').extract()[0]
            # temp['film_director'] = response.css('.post .persone::text').extract()[0]
            temp['genres_names'] = []
            for sel in response.css('td.genre p'):
                temp['genres_names'].append(sel.css('::text').extract()[0])
            for sel1 in response.css('.b-film-info'):
                temp['date'] = sel1.css('.name a::text').extract()[0]
                for sel2 in sel1.css('.b-film-list__li'):
                    temp['cinema'] = sel2.css('.film-name a::text').extract()[0]
                    for sel3 in sel2.css('.b-shedule-list .lists__li'):
                        item = SeanseItem()
                        item['beginning_at'] = sel3.css('.ticket::text').extract()[0]
                        item.update(temp)
                        yield item
        except IndexError:
            pass
