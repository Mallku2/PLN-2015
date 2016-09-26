# -*- coding: utf-8 -*-
from clustering.bag_of_words_rep.feature_selection import BagOfWordsRep
from clustering.clustering import KMeansClusteringComponent
import pdb


class MainPipeline(object):

    def __init__(self):
        # TODO: estoy inscrustando en el código el nombre del archivo...
        self._bag_of_words_rep = BagOfWordsRep("../bag_of_words_rep/globIndx")
        # TODO: quizás acá debería agregar código del constructor de
        # BagOfWords (aquel que lee los archivos en los que guardamos el
        # globalIndex...). Por cierto, no me parece que esté del todo
        # justificado que usemos una clase para implementar lo referido
        # a la construcción de la representación de un documento. Me parece
        # que tiene que ser más bien un simple método.
        #self._data_file = open("news.data", "ri+")
        self._clusters = KMeansClusteringComponent()
        # TODO: por ahora, pongo acá los primeros artículos, para procesamiento
        # posterior.
        self._first_articles = []
        self._first_articles_processed = False
        # TODO: para debuguear
        self._log = open("log", "ri+")
        # Determine if the file contains data.
        # TODO: revisar la forma en la que estoy almacenando la información
        self._data_file.seek(0, 2)  # Move file's pointer to its end.
        if self._data_file.tell() > 0:
            self._data_file.seek(0)
            # There should be a dictionary and a set, saved into _data_file.
            # Dictionary of the form {centroid X set of articles}.
            self._clustered_news = cPickle.load(self._data_file)
            # Set of links to the articles.
            self._scraped_news = cPickle.load(self._data_file)
            # Dictionary of the form {link to main article X time of the last
            # article added} (to implement "freezing" of old clusters)
            self._time_last_article_added = cPickle.load(self._data_file)
            # Erase data.
            self._data_file.seek(0)
            self._data_file.truncate()
        else:
            # {_data_file.tell() == 0}
            self._clustered_news = {}
            self._scraped_news = set()
            self._time_last_article_added = {}

    def open_spider(self, spider):
        self._log.write("open spider...")
        spider.set_scraped_news(self._clusters.get_scraped_news())

    def process_item(self, item, spider):
        resolved_link = item["resolved_link"]
        waiting_first_articles = False

        # TODO: como tenemos que esperar a las primeras 70 noticias...
        if len(self._scraped_news) < 70:
            waiting_first_articles = True

        if item["article_scraped"]:
            self._scraped_news.add(resolved_link)
            if waiting_first_articles:
                article = item["content"]
                self._first_articles.append(article)
                self._bag_of_words_rep.update_global_index_with_text(article)
            else:
                if not self._first_articles_processed:
                    for article in self._first_articles:
                        int_rep = self._bag_of_words_rep.\
                                        get_rep(article,
                                                waiting_first_articles)

                    self._first_articles_processed = True
                    # TODO: terminar!.

            # Save the time of this addittion, for clusters' freezing.
            # TODO: descomentar esta linea, cuando tenga calculado el centroid.
            # Por otro lado, si los centroides cambian cada vez que agrego
            # un artículo, voy a tener que eliminar entradas en este diccionario
            # que se corresponden con el viejo valor del centroide...
            #self._time_last_article_added[centroid] = time.time()
        else:
            # {not item["article_scraped"]}
            reason_not_scraped = item["reason_not_scraped"]
            if reason_not_scraped != 3:
                self._log.write("Enlace al artículo: " + item["resolved_link"] + "\n")
                self._log.write("Problema: " + str(reason_not_scraped) + "\n")
                self._log.write("*******************\n")
        return item

    def close_spider(self, spider):
        """cPickle.dump(self._clustered_news, self._data_file)
        cPickle.dump(self._scraped_news, self._data_file)
        cPickle.dump(self._time_last_article_added, self._data_file)
        self._data_file.close()"""
        self._log.close()
