# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScraperItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    body = scrapy.Field()
    is_main_article = scrapy.Field()
    cluster_id = scrapy.Field()
    article_scraped = scrapy.Field()
