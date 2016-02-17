# -*- coding: utf-8 -*-
import cPickle

class NewsScraperPipeline(object):

    def __init__(self):
        self._data_file = open("news.data", "w+")
        # Determine if the file contains data.
        self._data_file.seek(0, 2) # Move file's pointer to its end.
        if self._data_file.tell() > 0:
            self._data_file.seek(0, 0)
            # There should be a dictionary and a set, saved into _data_file.
            # Dictionary of the form {link X set of articles}.
            self._corpus = cPickle.load(self._data_file)
            # Set of links to the articles.
            self._scraped_news = cPickle.load(self._data_file)
            # Erase data.
            self._data_file.seek(0)
            self._data_file.truncate()
        else:
            # {_data_file.tell() == 0}
            self._corpus = {}
            self._scraped_news = set()

    def open_spider(self, spider):
        spider.set_scraped_news(self._scraped_news)

    def process_item(self, item, spider):
        if item["article_scraped"]:
            link = item["link"]
            self._scraped_news.add(link)
            cluster_id = item["cluster_id"]
            if item["is_main_article"]:
                self._corpus[cluster_id] = set()

            self._corpus[cluster_id].add((item["title"], item["body"]))

    def close_spider(self, spider):
        cPickle.dump(self._corpus, self._data_file)
        cPickle.dump(self._scraped_news, self._data_file)
        self._data_file.close()
