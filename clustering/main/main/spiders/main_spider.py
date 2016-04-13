# -*- coding: utf-8 -*-
import scrapy
import feedparser
import re
import cPickle
from bs4 import BeautifulSoup
from main.items import MainItem
from clustering.spider_utilities import selectors
from clustering.spider_utilities import common_utilities

class MainSpider(scrapy.Spider):
    name = "main_spider"
    # Extract the links to the rss service or each site
    start_urls = []
    for k, v in selectors.sites_selectors.iteritems():
        start_urls.append(v[selectors.rss_index])

    def __init__(self, *a, **kw):
        super(MainSpider, self).__init__(*a, **kw)
        # TODO: corregir esto y set_scraped_news
        self._scraped_news = None
        # Maintains a mapping between the urls of the main article of each
        # cluster, as taken from Google News (that is, not resolved), and
        # the resolved url of the article.
        self._main_articles = {}
        self._log = open("log_spider", "ri+")
        self._log.write("abriendo log_spider...")

    def set_scraped_news(self, scraped_news):
        self._scraped_news = scraped_news

    def parse(self, response):
        """Obtains the rss from a given news site (defined in start_urls).
            Parses it, and constructs the apropiate request for each article's link found.
        """
        self._log.write("Ya estamos en parse...")
        # TODO: posiblemente vamos a tener que limitarnos a tomar el rss de
        # cada diario (pensar en el caso de la nación: todos los días la portada
        # se ve diferente). Y sólo para casos específicos, leer el html del
        # portal (como pagina12, que no parece diferir mucho entre dia y dia)

        # TODO: estaría bueno guardar el xml obtenido, por cuestiones de debugging.
        # El tema es que debería poder saber el sitio que estoy consultando,
        # para guardar un xml con el nombre adecuado. Podríamos tratar de ver cual es
        # el método que llama a parse, para poder meter información en la request
        # sobre el sitio consultado
        requests = []
        rss = response.body
        rss_tree = feedparser.parse(rss)
        # Save the RSS, for debugging purposes.
        """rss_file = open("last_rss.xml", "ri+")
        rss_file.truncate()
        rss_file.write(rss)
        rss_file.close()"""
        for item in rss_tree.entries:
            # Extract the main article.
            link = item.link
            req = common_utilities.generate_appr_request(link, self.parse_article)
            if req:
                # Save its url (not resolved yet).
                req.meta["original_link"] = link
                # Arbitrary data, for debugging purposes
                req.meta["Debug"] = None
                requests.append(req)

        return requests

    def parse_article(self, response):
        """Extracts the title and the body of an article's html, using the XPATH
            selector saved into response.meta["body_selector"] and
            response.meta["title_selector"].
        """
        item = MainItem()
        item["article_scraped"] = False
        resolved_link = response.url
        item["resolved_link"] = resolved_link
        item["original_link"] = response.meta["original_link"]

        if resolved_link not in self._scraped_news:
            # Title
            title = common_utilities.extract_element(response, selectors.title_selector_index)
            if title:
                #item["title"] = text
                # Body
                body = common_utilities.extract_element(response, selectors.body_selector_index)
                if body:
                    item["content"] = title + "\n" + body
                    item["article_scraped"] = True
                else:
                    # {not body}
                    item["reason_not_scraped"] = 1 # Problem with body's selector
            else:
                # {not title}
                item["reason_not_scraped"] = 2 # Problem with title's selector
        else:
            # {resolved_link in self._scraped_news}
            item["reason_not_scraped"] = 3 # resolved_link already in self._scraped_news

        return item
