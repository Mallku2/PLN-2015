# -*- coding: utf-8 -*-
import scrapy
import feedparser
import cPickle
import re
from bs4 import BeautifulSoup
from news_scraper.items import NewsScraperItem
from clustering.spider_utilities.selectors import sites_selectors, title_selector_index, body_selector_index
from clustering.spider_utilities import common_utilities


class GoogleNewsSpider(scrapy.Spider):
    name = "google_news"
    start_urls = ["https://news.google.com/news?cf=all&hl=es&pz=1&ned=es_ar&output=rss"]

    def __init__(self, *a, **kw):
        super(GoogleNewsSpider, self).__init__(*a, **kw)
        self._scraped_news = None

    def set_scraped_news(self, scraped_news):
        self._scraped_news = scraped_news

    def get_rss(self):
        return self._rss

    def parse(self, response):
        """Obtains the rss from Google News. Parses it, and constructs the
            apropiate request for each article's link found.
        """
        requests = []
        self._rss = response.body
        rss_tree = feedparser.parse(self._rss)
        for item in rss_tree.entries:
            html_parser = BeautifulSoup(item.description, 'html.parser')
            # Find the link to the document that contains all the articles
            # related
            for a in html_parser.find_all('a'):
                link = a.attrs['href']
                site_reg_exp = ".*" + "http://news.google.com/news/story?" + ".*"
                match = re.search(site_reg_exp, link)
                if match:
                    requests.append(
                        scrapy.Request(link,
                                        callback=self._parse_main_document))
                    break

        return requests

    def _parse_main_document(self, response):
        requests = []
        # NOTE: extraigo los divs...
        divs = response.xpath("//div[@class=\"story-page-main\"]//div[@class=\"topic\"]//div[contains(@class, \"story\")]")
        for div in divs:
            # TODO: ahora solo nos hace falta usar una expresion xpath
            links = div.xpath("h2[@class=\"title\"]//a/@href")
            if len(links) != 1:
                self._log.write("Problemas intentando extraer los\
                enlaces a las noticias en " + response.url  + ": \
                h2 class = \"title\" no tiene la cantidad de enlaces\
                esperada.\n")
                break

            # {len(a) == 1}
            link = links[0].extract()
            req = common_utilities.generate_appr_request(link,
                                                self.parse_article)
            if req:
                req.meta["original_link"] = link
                # Arbitrary data, for debugging purposes
                req.meta["Debug"] = None
                # Obtain the id of the cluster.
                html_parser = BeautifulSoup(div.extract(), 'html.parser')
                # TODO: feo che...
                div_parsed = html_parser.find_all("div")[0]
                # TODO: solo nos haria falta BeautifulSoup para extraer el atributo
                # cid (porque no se como hacerlo con xpath). Para lo demas basta
                # con una expresion xpath...
                req.meta["cid"] = None
                for attr in div_parsed.attrs["class"]:
                    # TODO: esto quizas deberia estar en otro
                    # modulo
                    cluster_id_regexp = "cid-\d+"
                    match = re.search(cluster_id_regexp, attr)
                    if match:
                        req.meta["cid"] = attr
                        break

                if not req.meta["cid"]:
                    self._log.write("No se pudo extraer el cid del articulo " +\
                                    link + "\n")
                    req = None
                requests.append(req)

        return requests

    def parse_article(self, response):
        """Extracts the title and the body of an article's html, using the XPATH
            selector saved into response.meta["body_selector"] and
            response.meta["title_selector"].
        """
        item = NewsScraperItem()
        item["article_scraped"] = False
        resolved_link = response.url
        item["resolved_link"] = resolved_link
        item["original_link"] = response.meta["original_link"]
        item["cid"] = response.meta["cid"]

        if resolved_link not in self._scraped_news:
            # Title
            text = common_utilities.extract_element(response,
                                                    title_selector_index)
            if text:
                item["title"] = text

                # Body
                text = common_utilities.extract_element(response,
                                                        body_selector_index)
                if text:
                    item["body"] = text
                    item["article_scraped"] = True
                else:
                    # {not text}
                    # Problem with body's selector
                    item["reason_not_scraped"] = 1
            else:
                # {not text}
                item["reason_not_scraped"] = 2  # Problem with title's selector
        else:
            # {resolved_link in self._scraped_news}
            item["reason_not_scraped"] = 3  # resolved_link already in self._scraped_news

        return item
