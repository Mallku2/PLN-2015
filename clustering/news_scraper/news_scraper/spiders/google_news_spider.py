# -*- coding: utf-8 -*-
import scrapy
import feedparser
import re
import cPickle
from bs4 import BeautifulSoup
from news_scraper.items import NewsScraperItem
from selectors import sites_selectors


class GoogleNewsSpider(scrapy.Spider):
    name = "google_news"
    start_urls = ["https://news.google.com/news?cf=all&hl=es&pz=1&ned=es_ar&output=rss"]

    def __init__(self, *a, **kw):
        super(GoogleNewsSpider, self).__init__(*a, **kw)
        self._scraped_news = None
        # Maintains a mapping between the urls of the main atricle of each
        # cluster, as taken from Google News (that is, not resolved), and
        # the resolved url of the article.
        self._main_articles = {}

    def set_scraped_news(self, scraped_news):
        self._scraped_news = scraped_news

    def parse(self, response):
        """Obtains the rss from Google News. Parses it, and constructs the
            apropiate request for each article's link found.

            @url file:////home/mallku/Desktop/PLN/Prácticos/MaterialPractico4/Scraping/news_scraper/NoticiasDestacadasGoogleNoticias.xhtml
            @returns requests 28
            @scrapes title link body is_main_article cluster_id article_scraped
        """
        # TODO: revisar si es útil utilizar los contracts.
        requests = []
        rss = response.body
        rss_tree = feedparser.parse(rss)
        for item in rss_tree.entries:
            # Extract the main article.
            req = self.generate_appr_request(item.link)
            # TODO: las requests siempre se procesan en orden?, qué sucede
            # cuando una request no recibe respuesta a tiempo?.
            link_main_article = None
            if not req is None:
                req.meta["is_main_article"] = True
                # Save its url (not resolved yet).
                link_main_article = req.url
                self._main_articles[link_main_article] = None
                req.meta["link_main_article"] = link_main_article
            requests.append(req)

            # Continue with the related news, only if the main article
            # can be scraped.
            if not link_main_article is None:
                html_parser = BeautifulSoup(item.description, 'html.parser')
                for a in html_parser.find_all('a'):
                    req = self.generate_appr_request(a.attrs['href'])
                    if not req is None:
                        req.meta["is_main_article"] = False
                        req.meta["link_main_article"] = link_main_article
                    requests.append(req)

        return requests

    def generate_appr_request(self, link):
        """Analizes a string representing a link to a news' site,
            generates a request to that link and selects the apropiate callback
            method to handle the response. Also, saves the article into the
            corpus.

            PARAMS
            link: a string representing the link to the site.
            new_cluster: a boolean indicating if it is needed to create a new
            cluster in the corpus, or it must add the article to the actual
            cluster."""
        # TODO: re: determinar si esta forma de hacerlo es eficiente.
        req = None
        for site_reg_exp, selectors in sites_selectors.iteritems():
            match = re.search(site_reg_exp, link)
            if not match is None:
                req = scrapy.Request(link,
                                    callback=self.parse_specific_journal)
                req.meta["title_selector"] = selectors["title_selector"]
                req.meta["body_selector"] = selectors["body_selector"]
                break

        # TODO: fijarse cuando debo devolver return, y cuando yield.
        return req

    def parse_specific_journal(self, response):
        """Extracts the title and the body of an html article, using the XPATH
            selector saved into response.meta["body_selector"] and
            response.meta["title_selector"].
        """
        item = NewsScraperItem()
        item["article_scraped"] = False
        link = response.url

        if link not in self._scraped_news and response.status == 200:
            # This is an article not scraped yet.
            item["link"] = link

            if response.meta["is_main_article"]:
                item["is_main_article"] = True
                # Is the main article. Its url is resolved, and will be used
                # as id of its cluster. Also, we save it in a place available
                # for other calls of parse_specific_journal.
                item["cluster_id"] = response.url
                self._main_articles[response.meta["link_main_article"]] = response.url
            else:
                # {not response.meta["is_main_article"]}
                item["is_main_article"] = False
                item["cluster_id"] = self._main_articles[response.meta["link_main_article"]]

            # Determine if the cluster to which the article belongs is already
            # scraped.
            if not item["cluster_id"] is None:
                # Title.
                list_selector = response.xpath(response.meta["title_selector"]).extract()
                assert(len(list_selector) == 1)
                title_html = list_selector[0]
                title_parser = BeautifulSoup(title_html, 'html.parser')
                item["title"] = title_parser.get_text()

                # Body.
                list_selector = response.xpath(response.meta["body_selector"]).extract()
                assert(len(list_selector) == 1)
                body_html = list_selector[0]
                body_parser = BeautifulSoup(body_html, 'html.parser')
                item["body"] = body_parser.get_text()

                item["article_scraped"] = True

        return item
