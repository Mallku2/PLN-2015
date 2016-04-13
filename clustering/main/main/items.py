# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# TODO: creo un nuevo item, porque sospecho que el Item de news_scraper
# es demasiado específico para lo que hace esa araña
class MainItem(scrapy.Item):
    # TODO: nota: estos items quizás sólo requieran un único campo, ya que
    # cuando los analizamos para crear su representación como vectores, no
    # esperamos recibir 2 elementos distintos (título y cuerpo de noticia)
    content = scrapy.Field()
    article_scraped = scrapy.Field()
    resolved_link = scrapy.Field()
    reason_not_scraped = scrapy.Field()
    original_link = scrapy.Field()
