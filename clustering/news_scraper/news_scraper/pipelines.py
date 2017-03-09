# -*- coding: utf-8 -*-
import pickle


class NewsScraperPipeline(object):

    def __init__(self):
        # news.data has a dictionary representing the corpus (the clustered
        # news) and a dictionary with each scraped news.
        self._data_file = open("news.data", "r+b")
        self._log = open("log", "a+")
        self._log.write("\n-------------------------\n")
        self._log.write("Abriendo araña...\n")
        # For debugging...
        self._new_articles_added = False
        # Determine if the file contains data.
        self._data_file.seek(0, 2)  # Move file's pointer to its end.
        file_size = self._data_file.tell()
        if file_size > 0:
            self._data_file.seek(0)
            # There should be a dictionary and a set, saved into _data_file.
            # Dictionary of the form {link X set of articles}.
            self._corpus = pickle.load(self._data_file)
            # Set of links to the articles.
            self._scraped_news = pickle.load(self._data_file)
            # Erase data.
            self._data_file.seek(0)
            self._data_file.truncate()
            # Backup
            backup_file = open("news.data.backup." + str(file_size), "wb")
            pickle.dump(self._corpus, backup_file)
            pickle.dump(self._scraped_news, backup_file)
            backup_file.close()
        else:
            # {_data_file.tell() == 0}
            self._corpus = {}
            self._scraped_news = {}

    def open_spider(self, spider):
        spider.set_scraped_news(self._scraped_news)

    def process_item(self, item, spider):
        resolved_link = item["resolved_link"]
        if item["article_scraped"]:
            cluster_id = item["cid"]

            if cluster_id not in self._corpus:
                self._corpus[cluster_id] = {}

            # {cluster_id in self._corpus}
            self.add_article(cluster_id, item)
        else:
            # {not item["article_scraped"]}
            reason_not_scraped = item["reason_not_scraped"]
            if reason_not_scraped != 3:
                self._write_error_to_log(resolved_link,
                                         item["reason_not_scraped"])

        return item

    def _write_error_to_log(self, link, error_code):
        self._log.write("Enlace al articulo: " + link + "\n")
        self._log.write("Problema: " + str(error_code) + "\n")
        self._log.write("*******************\n")

    def add_article(self, cluster_id, item):
        """
            PRE : {cluster_id in self._corpus}
        """
        resolved_link = item["resolved_link"]
        title = item["title"]
        body = item["body"]
        self._corpus[cluster_id][resolved_link] = (title,
                                                   body)

        # TODO: realmente hace falta todo el item?
        self._scraped_news[resolved_link] = (item["cid"],
                                             title,
                                             body)

        # For debugging...
        self._new_articles_added = True

    def close_spider(self, spider):
        pickle.dump(self._corpus, self._data_file)
        pickle.dump(self._scraped_news, self._data_file)
        # For debugging...
        if self._new_articles_added:
            rss = spider.get_rss()
            rss_file = open("last_rss_" + str(len(self._scraped_news)) +
                            ".xml", "w")
            rss_file.write(rss)
            rss_file.close()

        self._data_file.close()
        self._log.write("Cerrando araña...")
        self._log.close()