from scipy.sparse import lil_matrix


class k_means_clustering_component:

    def __init__(self):
        self._centroids = set()
        self._documents = {}
        self._clustering_threshold = 0.4 # TODO: testear para determinar este valor
        # TODO: a continuacion deberiamos ubicar los primeros k-centroides?

    def add_and_cluster_new_document(self, document):
        """Applies the k-means algorithm to cluster the given document.
        """
        nrst_centroid = None
        dist_nrst_centroid = float("inf")
        # TODO: aparentemente, no me estaría haciendo falta el atributo
        # self._centroids
        for centroid in self._documents:
            # Calculate the distance between the centroid and the document
            dist = self._cosine_similarity(centroid, document)

            if dist < dist_nrst_centroid:
                dist_nrst_centroid = dist
                nrst_centroid = centroid

        if dist_nrst_centroid <= self._clustering_threshold:
            # Add the document to the nearest centroid found
            self._documents[nrst_centroid].add(document)
            documents = self._documents[nrst_centroid]

            # TODO: dada la interpretación que estoy haciendo del algoritmo
            # de clustering (ver notas), sólo nos haría falta redefinir
            # el centroide de este cluster.

            # As we added a new document, we must redefine its centroid
            new_centroid = lil_matrix((1))
            first_doc = True # Are we analyzing the first document?
            for document in documents:
                if first_doc:
                    # TODO: podría suceder que no todos los documentos tengan
                    # la misma forma?
                    # Yo estoy asumiendo que eso no es así
                    new_centroid = new_centroid.reshape(document.shape)
                    first_doc = False

                rows, cols = document.nonzero()
                for pos in zip(rows, cols):
                    new_centroid[pos] += document[pos]

            rows, cols = new_centroid.nonzero()
            length_cluster = len(documents)
            for pos in zip(rows, cols):
                new_centroid[pos] /= float(length_cluster)

            self._documents[new_centroid] = self._documents[nrst_centroid]
            self._documents.pop(nrst_centroid)

        else:
            # {dist_nrst_centroid > self._clustering_threshold}
            # The nearest centroid is further than the min. threshold.
            # Create a new cluster, with "document" as its centroid
            # TODO: aparentemente, no me estaría haciendo falta el atributo
            # self._centroids
            #self._centroids.add(document)
            self._documents[document] = set()
            self._documents[document].add(document)

    def _cosine_similarity(self, vect_1, vect_2):
        """Returns the cosine similarity between vect1 and vect2.
        PARAMS
        vect1, vect2: instances of scipy.sparse.lil_matrix."""
        l_vect1 = 0.0
        l_vect2 = 0.0
        dot_product = 0

        # Get the positions of the non-zero entries of one vector
        rows, cols = vect1.nonzero()

        for pos in zip(rows, cols):
            pos_1 = vect_1[pos]
            l_vect1 += pow(pos_1, 2.0)

            pos_2 = vect_2[pos]
            l_vect_2 += pow(pos_2, 2.0)

            dot_product += pos_1 * pos_2

        return dot_product / sqrt(pos_1 * pos_2)
