# -*- coding: utf-8 -*-
from threading import Thread
from scipy.sparse import dok_matrix
import pickle
import time
import sys
from math import sqrt
from clustering.bag_of_words_rep.feature_selection import VectRep


# TODO: hara falta tambien guardar aquí la longitud del vector?
# TODO: vamos a tener que agregar mas informcion en este objeto: url del rtic
class Document(object):
    def __init__(self, url, text, vec_rep):
        assert(isinstance(url, str))
        assert(isinstance(text, str))
        assert(isinstance(vec_rep, VectRep))

        self._url = url
        self._text = text
        self._vec_rep = vec_rep

    def get_text(self):
        return self._text

    def get_vec_rep(self):
        return self._vec_rep

    def get_vec_rep_length(self):
        return self._vec_rep.get_length()

    def get_url(self):
        return self._url


class Cluster(object):
    """Cluster of documents, with their centroid.
    """
    # TODO: la url la agrego por que es mi form de identificar y comparar cada
    # documento
    def __init__(self, url_cent, cent_text, cent_vec_rep, cluster_id):
        # TODO: me hace falta guardar el texto del centroide?
        assert(isinstance(cent_vec_rep, VectRep))
        self._cluster_id = cluster_id
        # TODO: agrego el cluster_id, para facilitar el debugging. Pero dejo
        # que desde el exterior se decida la forma de determinar el id
        self._centroid = cent_vec_rep
        self._documents = [Document(url_cent, cent_text, cent_vec_rep)]

    def add_document(self, url_doc, document, doc_vec_rep):
        self._documents.append(Document(url_doc, document, doc_vec_rep))
        # TODO: es eficiencte que siempre que agregue un nuevo documento,
        # me ponga a actualizar el centroide?.
        self._update_centroid(doc_vec_rep)
        # TODO: debugging
        self._check_property()

    # TODO: debugging
    def _cosine_similarity(self, vect_1, vect_2):
        """Returns the cosine similarity between vect1 and vect2.
        PARAMS
        vect_1 : instance of VecrRep.
        vect_2 : instance of VectRep."""

        l_vect_1 = vect_1.get_length()
        l_vect_2 = vect_2.get_length()

        assert(l_vect_1 > 0.0 and l_vect_2 > 0.0)

        dot_product = 0

        # Get the positions of the non-zero entries of vect_1
        if vect_1.get_dimensions() <= vect_2.get_dimensions():
            cols = vect_1.nonzero()
        else:
            # {vect_1.get_dimensions() > vect_2.get_dimensions()}
            cols = vect_2.nonzero()

        for pos in cols:
            dot_product += vect_1[pos] * vect_2[pos]

        return dot_product / (l_vect_1 * l_vect_2)

    # TODO: debugging
    def _check_property(self):
        for doc_1 in self._documents:
            for doc_2 in self._documents:
                if id(doc_1) != id(doc_2):
                    assert(self._cosine_similarity(doc_1.get_vec_rep(),
                           doc_2.get_vec_rep()) >= -0.68)
                    # TODO: debugging!
                    # sys.stdout.write("\rProperty passed!")
                    # sys.stdout.flush()

    def get_documents(self):
        return self._documents

    def get_centroid(self):
        return self._centroid

    def get_cluster_id(self):
        return self._cluster_id

    def get_size(self):
        return len(self._documents)

    # TODO: hace realmente falta este método, ahora que agregué un método para
    # alterar el centroide?
    def set_documents(self, documents):
        self._documents = documents

    # TODO: esto me parece que lo uso solo para tests...?
    def is_in_cluster_by_vector(self, doc_vec_rep):
        # TODO: solo me interesa preguntar por la representación vectorial?
        ret = False

        for doc_in_clstr in self._documents:
            ret = doc_vec_rep.is_equal_to(doc_in_clstr.get_vec_rep())
            if ret:
                break

        return ret

    def is_in_cluster_by_url(self, news_url):
        assert(isinstance(news_url, str))
        ret = False

        for doc_in_clstr in self._documents:
            ret = doc_in_clstr.get_url() == news_url
            if ret:
                break

        return ret

    def _update_centroid(self, new_vect):
        dim_new_vect = new_vect.get_dimensions()
        if dim_new_vect > self._centroid.get_dimensions():
            # TODO: si esto ocurre, no hay problema?
            self._centroid.resize(dim_new_vect)

        centroid_comp_sum = pow(self._centroid.get_length(), 2.0)
        size_cluster = float(self.get_size())
        cols = new_vect.nonzero()
        for pos in cols:
            centroid_comp_sum -= pow(self._centroid[pos], 2.0)
            self._centroid[pos] *= size_cluster
            self._centroid[pos] += new_vect[pos] / size_cluster
            centroid_comp_sum += pow(self._centroid[pos], 2.0)

        """cols = self._centroid.nonzero()
        sum_weights = 0.0
        for pos in cols:
            sum_weights += pow(self._centroid[pos], 2.0)"""

        # TODO: hace realmente falta tomar la raiz cuadrada?
        self._centroid.set_length(sqrt(centroid_comp_sum))



    """def _update_centroid(self):
        new_centroid = VectRep(1)
        centroid_dimensions = 1
        first_doc = True  # Are we analyzing the first document?
        for doc in self._documents:
            vec_rep = doc.get_vec_rep()
            dimensions = vec_rep.get_dimensions()
            if dimensions > centroid_dimensions:
                # TODO: si esto ocurre, no hay problema?
                new_centroid.resize(dimensions)
                centroid_dimensions = dimensions

            cols = vec_rep.nonzero()

            for pos in cols:
                new_centroid[pos] += vec_rep[pos]

        cols = new_centroid.nonzero()
        size_cluster = float(self.get_size())
        sum_weights = 0.0
        for pos in cols:
            new_centroid[pos] /= size_cluster
            sum_weights += pow(new_centroid[pos], 2.0)

        # TODO: hace realmente falta tomar la raiz cuadrada?
        new_centroid.set_length(sqrt(sum_weights))
        # TODO: me parece que esto me esta mostrando que no necesito
        # para nada que _centroid sea una instancia de Document.
        # Me basta con que sea un VectRep...
        self._centroid = new_centroid"""

    # TODO: revisar si esta es la mejor form de implementar la iteración sobre
    # los documentos
    def __iter__(self):
        self._documents_iterator = iter(self._documents)
        return self

    def __next__(self):
        return next(self._documents_iterator)


class Clusters(object):
    # TODO: debería hacerlo iterativo esto????
    def __init__(self, data_file_name):
        self._log_file = open("ClusterLog", "a")
        self._log_file.write("Abriendo ClusterLog\n")
        self._data_file = open(data_file_name, "r+b")

        # Determine if the file contains data.
        # Move the file's pointer 0 bytes from the end of the stream
        # (whence == 2): move file's pointer to the end of the file.
        # Returns the new position of the file's pointer.
        if self._data_file.seek(0, 2) > 0:
            self._log_file.write("data_tests tenia informacion\n")
            # The file has data. Return the file's pointer to the beginning.
            self._data_file.seek(0)
            # There should be a dictionary and a set, saved into _data_file.
            # Dictionary of the form:
            # {centro_id X (centroid_data, set of (article_vec_rep, article)}.
            self._clusters = pickle.load(self._data_file)
            # Set of links to the articles.
            self._scraped_news = pickle.load(self._data_file)
            # Dictionary of the form {link to main article X time of the last
            # article added} (to implement "freezing" of old clusters)
            self._time_last_article_added = pickle.load(self._data_file)
            # Erase data.
            self._data_file.seek(0)
            self._data_file.truncate()
        else:
            # {self._data_file.seek(0, 2) == 0}
            self._log_file.write("data_tests NO tenia informacion\n")
            self._clusters = {}
            self._scraped_news = set()
            self._time_last_article_added = {}

    def get_cluster(self, cluster_id):
        return self._clusters[cluster_id]

    def add_document(self, cluster_id, url_doc, doc_vec_rep,
                     document):
        self._clusters[cluster_id].add_document(url_doc, document, doc_vec_rep)
        # TODO: realmente me hace falta cambiar el id?
        """new_centroid = self._clusters[cluster_id].get_centroid()
        # TODO: alguna razón para utilizar el id de un centroide como clave?
        self._clusters[id(new_centroid)] = self._clusters[cluster_id]
        self._clusters.pop(cluster_id)"""

    def add_new_cluster(self, url_doc, document, doc_vec_rep):
        assert(isinstance(doc_vec_rep, VectRep))
        self._clusters[url_doc] = Cluster(url_doc, document, doc_vec_rep,
                                          url_doc)

    def get_clusters_quantity(self):
        return len(self._clusters)

    def save_clusters(self):
        """NOTE: from
        https://docs.python.org/3/reference/datamodel.html: "It is not
        guaranteed that __del__() methods are called for objects that still
        exist when the interpreter exits"
        """
        pickle.dump(self._clusters, self._data_file)
        # TODO: al picklear este set salta el SEGFAULT!
        pickle.dump(self._scraped_news, self._data_file)
        pickle.dump(self._time_last_article_added, self._data_file)
        self._data_file.close()
        self._log_file.close()

    # TODO: revisar si esta es la mejor form de implementar la iteración sobre
    # Clusters
    def __iter__(self):
        self._clusters_iterator = iter(self._clusters.values())
        return self

    def __next__(self):
        return next(self._clusters_iterator)


class KMeansClusteringComponent(object):

    def __init__(self, data_file_name, clustering_threshold):
        self._log_file = open("ClustersLog", "a")
        self._log_file.write("Abriendo ClustersLog\n")
        self._clusters = Clusters(data_file_name)
        self._log_file.write("Instancia De Clusters creada\n")
        # TODO: testear para determinar este valor
        self._clustering_threshold = clustering_threshold
        # TODO: a continuacion deberiamos ubicar los primeros k-centroides?

    def add_document(self, url_doc, document, doc_vec_rep):
        # TODO: por que no realizo aquí la construcción de la representación
        # vectorial?
        """Applies the k-means algorithm to cluster the given document.

            PARAMS
            doc_vec_rep: VectRep, bag-of-words representation of an article.
        """
        nrst_centroid = None
        dist_nrst_centroid = float("-inf")
        l_document = doc_vec_rep.get_length()

        for cluster in self._clusters:
            centroid = cluster.get_centroid()
            # Calculate the distance between the centroid and the document
            dist = self._cosine_similarity(centroid, doc_vec_rep)

            if dist > dist_nrst_centroid:
                dist_nrst_centroid = dist
                nrst_centroid = cluster.get_cluster_id()

        if dist_nrst_centroid >= self._clustering_threshold:
            # Add the document to the nearest centroid found
            # TODO: dada la interpretación que estoy haciendo del algoritmo
            # de clustering (ver notas), sólo nos haría falta redefinir
            # el centroide de este cluster.

            # As we added a new document, we must redefine its centroid
            self._clusters.add_document(nrst_centroid, url_doc, doc_vec_rep,
                                        document)

        else:
            # {dist_nrst_centroid < self._clustering_threshold}
            # The nearest centroid is further than the min. threshold.
            # Create a new cluster, with "document" as its centroid
            self._clusters.add_new_cluster(url_doc, document, doc_vec_rep)

    def get_clusters(self):
        return self._clusters

    def get_clustering_threshold(self):
        return self._clustering_threshold

    def get_scraped_news(self):
        return self._scraped_news

    def get_clusters_quantity(self):
        return self._clusters.get_clusters_quantity()

    def save_clusters(self):
        self._clusters.save_clusters()

    def get_cluster_from_news_url(self, news_url):
        assert(isinstance(news_url, str))
        ret = None

        for cluster in self._clusters:
            if cluster.is_in_cluster_by_url(news_url):
                ret = cluster
                break

        return ret

    def _cosine_similarity(self, vect_1, vect_2):
        """Returns the cosine similarity between vect1 and vect2.
        PARAMS
        vect_1 : instance of VecrRep.
        vect_2 : instance of VectRep."""

        l_vect_1 = vect_1.get_length()
        l_vect_2 = vect_2.get_length()

        assert(l_vect_1 > 0.0 and l_vect_2 > 0.0)

        dot_product = 0

        # Get the positions of the non-zero entries of vect_1
        if vect_1.get_dimensions() <= vect_2.get_dimensions():
            cols = vect_1.nonzero()
        else:
            # {vect_1.get_dimensions() > vect_2.get_dimensions()}
            cols = vect_2.nonzero()

        for pos in cols:
            dot_product += vect_1[pos] * vect_2[pos]

        return dot_product / (l_vect_1 * l_vect_2)


# TODO: primera implementación de un hilo consumidor de vectores, desde
# una cola thread-safe
class ThreadedKMeansClusteringComponent(Thread):
    def __init__(self, queue, data_file_name, sentinel_value):
        """
        PARAMS

        queue : an instance of Queue
                (https://docs.python.org/3.5/library/queue.html)
        """
        self._queue = queue
        self._clustering_component = KMeansClusteringComponent(data_file_name)
        self._articles_available = True
        self._sentinel_value = sentinel_value
        Thread.__init__(self)

    def run(self):
        # TODO: este mecanismo de corte es dependiente del tipo de test
        # que estoy realizando...
        articles_processed = 1
        while self._articles_available:
            # Block until an element is available in the queue
            url_article, text, vect_rep = self._queue.get(block=True)

            # Check against the sentinel value
            if url_article != self._sentinel_value:
                self._clustering_component.add_document(url_article,
                                                        text,
                                                        vect_rep)
                sys.stdout.write("\rClustering - articles processed:%d" % articles_processed)
                sys.stdout.flush()
                articles_processed += 1
            else:
                # {url_article == self._sentinel_value}
                self._articles_available = False
