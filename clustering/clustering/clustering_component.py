# -*- coding: utf-8 -*-
from scipy.sparse import dok_matrix
from math import sqrt

class KMeansClusteringComponent(object):

    def __init__(self):
        self._centroids = set()
        self._documents = {}
        self._clustering_threshold = 0.4 # TODO: testear para determinar este valor
        # TODO: a continuacion deberiamos ubicar los primeros k-centroides?

    def add_and_cluster_new_document(self, new_document):
        """Applies the k-means algorithm to cluster the given document.

            PARAMS
            document: dok_matrix, bag-of-words representation of an article.
        """
        nrst_centroid = None
        dist_nrst_centroid = float("-inf")

        rows, cols = new_document.nonzero()
        summatory = 0.0
        for pos in zip(rows, cols):
            summatory += pow(new_document[pos], 2.0)

        l_document = sqrt(summatory)

        for k, v in self._documents.items():
            # Calculate the distance between the centroid and the document
            centroid_data = v[0]
            dist = self._cosine_similarity(centroid_data[0], centroid_data[1],
                                           new_document, l_document)

            if dist > dist_nrst_centroid:
                dist_nrst_centroid = dist
                nrst_centroid = k

        if dist_nrst_centroid >= self._clustering_threshold:
            # Add the document to the nearest centroid found
            # self._documents[nrst_centroid][1].append(new_document)
            documents = self._documents[nrst_centroid][1]
            documents.append(new_document)

            # TODO: dada la interpretación que estoy haciendo del algoritmo
            # de clustering (ver notas), sólo nos haría falta redefinir
            # el centroide de este cluster.

            # As we added a new document, we must redefine its centroid
            new_centroid = dok_matrix((1,1))
            centroid_dimensions = 1
            first_doc = True # Are we analyzing the first document?
            for document in documents:
                dimensions = document.shape[1]
                if dimensions > centroid_dimensions:
                    # TODO: si esto ocurre, no hay problema?
                    new_centroid.resize(document.shape)
                    centroid_dimensions = dimensions

                rows, cols = document.nonzero()

                for pos in zip(rows, cols):
                    new_centroid[pos] += document[pos]

            rows, cols = new_centroid.nonzero()
            length_cluster = len(documents)
            length_centroid = 0.0
            for pos in zip(rows, cols):
                new_centroid[pos] /= float(length_cluster)
                length_centroid += pow(new_centroid[pos], 2.0)

            # NOTE: the ugliness of this data structure is the result from the
            # fact that lil_matrix cannot be reshaped (in the way needed)
            # in version 0.18 of scipy, nor be used as index of dictionaries
            # (which was possible in 0.17). Now I need to use dok_matrix, which
            # also are not hashables, so they cannot be index of dictionaries.
            new_centroid_data = (new_centroid, length_centroid)
            self._documents[id(new_centroid)] = (new_centroid_data, documents)
            self._documents.pop(nrst_centroid)

        else:
            # {dist_nrst_centroid < self._clustering_threshold}
            # The nearest centroid is further than the min. threshold.
            # Create a new cluster, with "document" as its centroid
            centroid_data = (new_document, l_document)
            self._documents[id(new_document)] = (centroid_data, [new_document])

    def get_documents(self):
        return self._documents

    def get_clustering_threshold(self):
        return self._clustering_threshold

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
