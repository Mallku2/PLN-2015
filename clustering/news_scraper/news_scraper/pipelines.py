# -*- coding: utf-8 -*-
import cPickle
import time
import pdb # TODO: eliminar

class NewsScraperPipeline(object):

    def __init__(self):
        # TODO: cambiar el nombre de este archivo...
        self._data_file = open("news.data", "ri+")
        self._log = open("log", "a+")
        # For debugging...
        self._new_articles_added = False
        # Determine if the file contains data.
        self._data_file.seek(0, 2) # Move file's pointer to its end.
        if self._data_file.tell() > 0:
            self._data_file.seek(0)
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
            # TODO: con la nueva forma de referirnos al id del cluster, no
            # me va a hacer mas falta que add_article reciba por separado el
            # id de cluster
            self.add_article(cluster_id, item)
        else:
            # {not item["article_scraped"]}
            self._write_error_to_log(item["resolved_link"],
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
        # TODO: quizas no haga falta almacenar el titulo separado del cuerpo...
        # TODO: quizas deberiamos traer aqui la labor de agregar una nueva
        # clave a self._corpus
        # TODO: no esta feo meterse con los indices?
        # TODO: recordar que ya no hace falta hacer tanto despelote con
        # el cluster_id. Quizas ya no haga falta recibirlo por parametro.
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
        cPickle.dump(self._corpus, self._data_file)
        cPickle.dump(self._scraped_news, self._data_file)
        # For debugging...
        if self._new_articles_added:
            rss = spider.get_rss()
            rss_file = open("last_rss_" + str(len(self._scraped_news)) + ".xml",
                            "w")
            rss_file.write(rss)
            rss_file.close()

        self._data_file.close()
        self._log.close()
