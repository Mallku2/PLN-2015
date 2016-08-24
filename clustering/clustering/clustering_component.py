# -*- coding: utf-8 -*-
from scipy.sparse import dok_matrix
import pickle
from math import sqrt


# TODO: abstraer Centroid!. O puede ser un caso especial de la instancia
# Document?
# TODO: hara falta tambien guardar aquí la longitud del vector?
# TODO: a los fines de debugging,  me resulta conveniente que los documentos
# tengan referencias al cluster al que pertenecen...
class Document(object):
    def __init__(self, text, vec_rep, vec_rep_length):
        assert(isinstance(vec_rep, dok_matrix))
        self._text = text
        self._vec_rep = vec_rep
        self._vec_rep_length = vec_rep_length

    def get_text(self):
        return self._text

    def get_vec_rep(self):
        return self._vec_rep

    def get_vec_rep_length(self):
        return self._vec_rep_length


class Cluster(object):
    """Cluster of documents, with their centroid.
    """
    def __init__(self, cent_text, cent_vec_rep, cent_length, cluster_id):
        # TODO: me hace falta guardar el texto del centroide?
        assert(isinstance(cent_vec_rep, dok_matrix))
        # TODO: agrego el cluster_id, para facilitar el debugging. Pero dejo
        # que desde el exterior se decida la forma de determinar el id
        self._cluster_id = cluster_id
        centroid = Document(cent_text, cent_vec_rep, cent_length)
        self._centroid = centroid
        self._documents = set()
        self._documents.add(centroid)

    def add_document(self, document, doc_vec_rep, len_vec_rep):
        self._documents.add(Document(document, doc_vec_rep, len_vec_rep))
        self._update_centroid()

    def get_documents(self):
        return self._documents

    def get_centroid(self):
        return self._centroid

    def get_size(self):
        return len(self._documents)

    def get_cluster_id(self):
        return self._cluster_id

    # TODO: hace realmente falta este método, ahora que agregué un método para
    # alterar el centroide?
    def set_documents(self, documents):
        self._documents = documents

    # TODO: parece que ya no hace falta este método
    def set_centroid(self, cent_vect_rep, cent_length):
        self._centroid = Document("", cent_vec_rep, cent_length)

    def _update_centroid(self):
        new_centroid = dok_matrix((1, 1))
        centroid_dimensions = 1
        first_doc = True  # Are we analyzing the first document?
        for doc in self._documents:
            vec_rep = doc.get_vec_rep()
            dimensions = vec_rep.shape[1]
            if dimensions > centroid_dimensions:
                # TODO: si esto ocurre, no hay problema?
                new_centroid.resize(vec_rep.shape)
                centroid_dimensions = dimensions

            rows, cols = vec_rep.nonzero()

            for pos in zip(rows, cols):
                new_centroid[pos] += vec_rep[pos]

        rows, cols = new_centroid.nonzero()
        size_cluster = float(self.get_size())
        sum_weights = 0.0
        for pos in zip(rows, cols):
            new_centroid[pos] /= size_cluster
            sum_weights += pow(new_centroid[pos], 2.0)

        # TODO: hace realmente falta tomar la raiz cuadrada?
        self._centroid = Document("", new_centroid, sqrt(sum_weights))

    # TODO: revisar si esta es la mejor form de implementar la iteración sobre
    # los documentos
    def __iter__(self):
        self._documents_iterator = iter(self._documents)
        return self

    def __next__(self):
        return next(self._documents_iterator)


class Clusters(object):
    # TODO: debería hacerlo iterativo esto????
    def __init__(self, data_file):
        self._data_file = open(data_file, "r+b")
        # Determine if the file contains data.
        self._data_file.seek(0, 2)  # Move file's pointer to its end.
        if self._data_file.tell() > 0:
            self._data_file.seek(0)
            # There should be a dictionary and a set, saved into _data_file.
            # Dictionary of the form:
            # {centro_id X (centroid_data, set of (article_vec_rep, article)}.
            self._clusters = pickle.load(self._data_file)
            # Dictionary of the form {centro_id X (centroid, centroid_length)}
            self._centroids = pickle.load(self._data_file)
            # Set of links to the articles.
            self._scraped_news = pickle.load(self._data_file)
            # Dictionary of the form {link to main article X time of the last
            # article added} (to implement "freezing" of old clusters)
            self._time_last_article_added = pickle.load(self._data_file)
            # Erase data.
            self._data_file.seek(0)
            self._data_file.truncate()
        else:
            # {_data_file.tell() == 0}
            self._clusters = {}
            self._centroids = {}
            self._scraped_news = set()
            self._time_last_article_added = {}

    def get_cluster(self, cluster_id):
        return self._clusters[cluster_id]

    def add_document(self, cluster_id, doc_vec_rep, len_vec_rep, document):
        self._clusters[cluster_id].add_document(document, doc_vec_rep,
                                                len_vec_rep)
        new_centroid = self._clusters[cluster_id].get_centroid()
        # TODO: alguna razón para utilizar el id de un centroide como clave?
        self._clusters[id(new_centroid)] = self._clusters[cluster_id]
        self._clusters.pop(cluster_id)

    def add_new_cluster(self, document, doc_vec_rep, l_document):
        assert(isinstance(doc_vec_rep, dok_matrix))

        cluster_id = id(doc_vec_rep)
        self._clusters[cluster_id] = Cluster(document, doc_vec_rep,
                                             l_document, cluster_id)

    def get_length(self):
        return len(self._clusters)

    # TODO: revisar si esta es la mejor form de implementar la iteración sobre
    # Clusters
    def __iter__(self):
        self._clusters_iterator = iter(self._clusters.values())
        return self

    def __next__(self):
        return next(self._clusters_iterator)

    def __del__(self):
        pickle.dump(self._clusters, self._data_file)
        pickle.dump(self._centroids, self._data_file)
        pickle.dump(self._scraped_news, self._data_file)
        pickle.dump(self._time_last_article_added, self._data_file)
        self._data_file.close()


class KMeansClusteringComponent(object):

    def __init__(self, data_file):
        self._clusters = Clusters(data_file)
        # TODO: testear para determinar este valor
        self._clustering_threshold = 0.4
        # TODO: a continuacion deberiamos ubicar los primeros k-centroides?

    def add_document(self, document, doc_vec_rep, len_vec_rep):
        # TODO: por que no realizo aquí la construcción de la representación
        # vectorial?
        """Applies the k-means algorithm to cluster the given document.

            PARAMS
            doc_vec_rep: dok_matrix, bag-of-words representation of an article.
        """
        nrst_centroid = None
        dist_nrst_centroid = float("-inf")

        rows, cols = doc_vec_rep.nonzero()
        summatory = 0.0
        # TODO: esto se puede escribir en una sola linea
        for pos in zip(rows, cols):
            summatory += pow(doc_vec_rep[pos], 2.0)
        # TODO: hace falta calcular sqrt?
        l_document = sqrt(summatory)
        for cluster in self._clusters:
            centroid = cluster.get_centroid()
            # Calculate the distance between the centroid and the document
            dist = self._cosine_similarity(centroid.get_vec_rep(),
                                           centroid.get_vec_rep_length(),
                                           doc_vec_rep, l_document)

            if dist > dist_nrst_centroid:
                dist_nrst_centroid = dist
                nrst_centroid = cluster.get_cluster_id()

        if dist_nrst_centroid >= self._clustering_threshold:
            # Add the document to the nearest centroid found
            # TODO: dada la interpretación que estoy haciendo del algoritmo
            # de clustering (ver notas), sólo nos haría falta redefinir
            # el centroide de este cluster.

            # As we added a new document, we must redefine its centroid
            self._clusters.add_document(nrst_centroid, doc_vec_rep, l_document,
                                        document)

        else:
            # {dist_nrst_centroid < self._clustering_threshold}
            # The nearest centroid is further than the min. threshold.
            # Create a new cluster, with "document" as its centroid
            self._clusters.add_new_cluster(document, doc_vec_rep, l_document)

    def get_clusters(self):
        return self._clusters

    def get_clustering_threshold(self):
        return self._clustering_threshold

    def get_scraped_news(self):
        return self._scraped_news

    def get_clusters_quantity(self):
        return self._clusters.get_length()

    def _cosine_similarity(self, vect_1, l_vect_1, vect_2, l_vect_2):
        """Returns the cosine similarity between vect1 and vect2.
        PARAMS
        vect_1 : instance of scipy.sparse.dok_matrix, of 1xn dimensions.
        vect_2 : instance of scipy.sparse.dok_matrix, of 1xn dimensions.
        l_vect_1 : length of vect_1
        l_vect_2 : length of vect_2"""
        dot_product = 0

        # Get the positions of the non-zero entries of vect_1
        rows, cols = vect_1.nonzero()

        for pos in zip(rows, cols):
            dot_product += vect_1[pos] * vect_2[pos]

        return dot_product / (l_vect_1 * l_vect_2)
