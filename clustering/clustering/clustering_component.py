# -*- coding: utf-8 -*-
import pickle
from math import sqrt


class Document(object):
    def __init__(self, url, text, vec_rep):
        assert(isinstance(url, str))
        assert(isinstance(text, str))

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
    def __init__(self, url_cent, cent_text, cent_vec_rep, cluster_id,
                 centroid_type):

        self._cluster_id = cluster_id
        self._centroid = cent_vec_rep
        self._documents = [Document(url_cent, cent_text, cent_vec_rep)]
        self._centroid_type = centroid_type

    def add_document(self, url_doc, document, doc_vec_rep):
        self._documents.append(Document(url_doc, document, doc_vec_rep))
        self._update_centroid(doc_vec_rep)

    def get_documents(self):
        return self._documents

    def get_centroid(self):
        return self._centroid

    def get_cluster_id(self):
        return self._cluster_id

    def get_size(self):
        return len(self._documents)

    def is_in_cluster_by_vector(self, doc_vec_rep):
        """For testing purposes
        """

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
        centroid_length_2 = pow(self._centroid.get_length(), 2.0)
        size_cluster = float(self.get_size())
        cols_new_vect = None

        if self._centroid_type == 1:
            dim_new_vect = new_vect.get_dimensions()
            if dim_new_vect > self._centroid.get_dimensions():
                self._centroid.resize(dim_new_vect)

            cols_new_vect = new_vect.nonzero()

        else:
            # {self._centroid_type != 1}
            cols_new_vect = [pos for pos in new_vect.nonzero() if pos
                             in self._centroid.nonzero()]

        for pos in cols_new_vect:
            centroid_length_2 -= pow(self._centroid[pos], 2.0)
            self._centroid[pos] *= (size_cluster - 1.0)
            self._centroid[pos] += new_vect[pos]
            self._centroid[pos] /= size_cluster
            centroid_length_2 += pow(self._centroid[pos], 2.0)

        # Updates components for the remaining non-zero elements of centroid
        cols_centroid = [pos for pos in self._centroid.nonzero() if pos
                         not in cols_new_vect]

        for pos in cols_centroid:
            centroid_length_2 -= pow(self._centroid[pos], 2.0)
            self._centroid[pos] *= (size_cluster - 1.0)
            self._centroid[pos] /= size_cluster
            centroid_length_2 += pow(self._centroid[pos], 2.0)

        self._centroid.set_length(sqrt(centroid_length_2))

    def __iter__(self):
        self._documents_iterator = iter(self._documents)
        return self

    def __next__(self):
        return next(self._documents_iterator)


class Clusters(object):
    def __init__(self, data_file_name, centroid_type):
        self._log_file = open("ClusterLog", "a")
        self._log_file.write("Abriendo ClusterLog\n")
        self._data_file = open(data_file_name, "r+b")
        self._centroid_type = centroid_type

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

    def add_new_cluster(self, url_doc, document, doc_vec_rep):
        self._clusters[url_doc] = Cluster(url_doc, document, doc_vec_rep,
                                          url_doc, self._centroid_type)

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

    def __iter__(self):
        self._clusters_iterator = iter(self._clusters.values())
        return self

    def __next__(self):
        return next(self._clusters_iterator)


class KMeansClusteringComponent(object):

    def __init__(self, data_file_name, clustering_threshold, centroid_type):
        self._log_file = open("ClustersLog", "a")
        self._log_file.write("Abriendo ClustersLog\n")
        self._clusters = Clusters(data_file_name, centroid_type)
        self._log_file.write("Instancia De Clusters creada\n")
        self._clustering_threshold = clustering_threshold

    def add_document(self, url_doc, document, doc_vec_rep):
        """Applies the k-means algorithm to cluster the given document.

            PARAMS
            doc_vec_rep: VectRep, bag-of-words representation of an article.
        """
        added = False

        for cluster in self._clusters:
            centroid = cluster.get_centroid()
            # Calculate the distance between the centroid and the document
            dist = centroid.cosine_similarity(doc_vec_rep)

            if dist >= self._clustering_threshold:
                # As we added a new document, we must redefine its centroid
                self._clusters.add_document(cluster.get_cluster_id(), url_doc,
                                            doc_vec_rep, document)
                added = True
                break

        if not added:
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
