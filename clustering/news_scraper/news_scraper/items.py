# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScraperItem(scrapy.Item):
    title = scrapy.Field()
    body = scrapy.Field()
    resolved_link = scrapy.Field()
    original_link = scrapy.Field()
    # Cluster id
    cid = scrapy.Field()
    article_scraped = scrapy.Field()
    reason_not_scraped = scrapy.Field()
