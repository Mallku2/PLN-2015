# -*- coding: utf-8 -*-
from clustering.bag_of_words_rep.feature_selection import VectRep,\
    BagOfWordsRep, ThreadedBagOfWordsRep
import pickle
import sys
import time
from unittest import TestCase
from math import sqrt
from queue import Queue
from clustering_component import KMeansClusteringComponent, Cluster,\
    ThreadedKMeansClusteringComponent


tests_file = "data_tests"


class TestClustering(TestCase):

    def setUp(self):
        self._clustering_component_1 = KMeansClusteringComponent(tests_file,
                                                                 0.2)
        self._clustering_component_2 = KMeansClusteringComponent(tests_file,
                                                                 0.25)
        self._clustering_component_3 = KMeansClusteringComponent(tests_file,
                                                                 0.3)
        self._clustering_component_4 = KMeansClusteringComponent(tests_file,
                                                                 0.4)
        self._clustering_component_5 = KMeansClusteringComponent(tests_file,
                                                                 0.5)

    def tearDown(self):
        f = open(tests_file, "w")
        f.truncate()
        f.close()

    # TODO: resolver el asunto con save_clusters!
    def test_save_clusters(self):
        """vector_1 = VectRep(2)
        vector_1[0] = 0
        vector_1[1] = 2
        vector_1.set_length(2)
        self._clustering_component_1.add_document("", "", vector_1)
        self._clustering_component_1.save_clusters()

        self._clustering_component = KMeansClusteringComponent(tests_file)
        clusters = self._clustering_component.get_clusters()

        # There is just one cluster...
        self.assertEqual(clusters.get_length(), 1)

        # That cluster has length 1, and vector_1 is in the cluster...
        for cluster in clusters:
            self.assertEqual(cluster.get_size(), 1)
            self.assertTrue(cluster.is_in_cluster(vector_1))"""

    def test_calculate_new_centroid(self):
        # TODO: terminar de escribir test mas interesantes
        # Cluster with one document
        vec_1 = VectRep(2)
        vec_1[0] = 0
        vec_1[1] = 0
        vec_1.set_length(0)
        cluster = Cluster("", "", vec_1, id(vec_1))
        centroid = cluster.get_centroid()

        self.assertEqual(centroid.get_length(), 0)
        self.assertTrue(centroid.is_equal_to(vec_1))

        # Add a new document
        vec_2 = VectRep(2)
        vec_2[0] = 1
        vec_2[1] = 1
        vec_2.set_length(sqrt(2))
        cluster.add_document("", "", vec_2)
        centroid = cluster.get_centroid()

        # Check length
        correct_l = sqrt(pow((0 + 1) / 2.0, 2) + pow((0 + 1) / 2.0, 2))
        self.assertAlmostEqual(centroid.get_length(), correct_l)

        # Check centroid
        vec_3 = VectRep(2)
        vec_3[0] = (0 + 1) / 2.0
        vec_3[1] = (0 + 1) / 2.0
        self.assertTrue(vec_3.is_equal_to(centroid))

    def test_add_vectors(self):
        # TODO: como ya tengo otro test hecho para saber si calculo bien el
        # centroide, aca solo me deberia concentrar en ver si estoy escogiendo
        # adecuadamente el cluster en donde ubico un nuevo documento.
        vector_1 = VectRep(2)
        vector_1[0] = 0
        vector_1[1] = 2
        vector_1.set_length(2)
        self._clustering_component_1.add_document("", "", vector_1)
        clusters = self._clustering_component_1.get_clusters()

        # There is just one cluster...
        self.assertEqual(clusters.get_clusters_quantity(), 1)

        # That cluster has length 1, and vector_1 is in the cluster...
        for cluster in clusters:
            self.assertEqual(cluster.get_size(), 1)
            self.assertTrue(cluster.is_in_cluster_by_vector(vector_1))

        # Add a new vector, which is close enough to conform a cluster with
        # the previous vector.
        vector_2 = VectRep(2)
        vector_2[0] = 0
        vector_2[1] = 2
        vector_2.set_length(2)
        self._clustering_component_1.add_document("", "", vector_2)
        self.assertEqual(clusters.get_clusters_quantity(), 1)

        # That one cluster has length 2, and vector_2 is in the cluster...
        for cluster in clusters:
            self.assertEqual(cluster.get_size(), 2)
            self.assertTrue(cluster.is_in_cluster_by_vector(vector_1))
            self.assertTrue(cluster.is_in_cluster_by_vector(vector_2))

        # Add a vector that is orthogonal to the previous ones
        vector_3 = VectRep(2)
        vector_3[0] = 2
        vector_3[1] = 0
        vector_3.set_length(2)
        self._clustering_component_1.add_document("new_vector", "", vector_3)
        self.assertEqual(self._clustering_component_1.get_clusters_quantity(), 2)

        for cluster in clusters:
            cluster_size = cluster.get_size()
            if cluster_size == 1:
                # Then, vector_3 must be its unique member...
                self.assertTrue(cluster.is_in_cluster_by_vector(vector_3))
            else:
                # {cluster_size != 1}
                self.assertEqual(cluster_size, 2)
                self.assertTrue(cluster.is_in_cluster_by_vector(vector_1))
                self.assertTrue(cluster.is_in_cluster_by_vector(vector_2))

    def test_against_google_news(self):
        corpus_file = open("news.data", "rb")
        clustered_news = pickle.load(corpus_file)
        news = pickle.load(corpus_file)

        glob_index_file_name = "globIndexTest"
        # Prepare an empty global index
        glob_index_file = open(glob_index_file_name, "wb")
        # {Word x frequency in the whole collection}
        pickle.dump({}, glob_index_file)
        # Collection size
        pickle.dump(0, glob_index_file)
        # Amount of words into the collection
        pickle.dump(0, glob_index_file)
        # {Word x position of the word (dimension) into the sparse vector that
        # represents each document}
        pickle.dump({}, glob_index_file)
        glob_index_file.close()

        bag_of_words_rep = BagOfWordsRep(glob_index_file_name)

        articles_processed = 0
        first_articles_processed = False
        first_articles = []

        for url_news, data in news.items():
            cluster_id, title, body = data
            text = title + "\n" + body

            if articles_processed < 70:
                # Just update the global index
                bag_of_words_rep.update_global_index_with_text(text)
                articles_processed += 1
                first_articles.append((url_news, text))
            else:
                # {articles_processed >= 70}
                if not first_articles_processed:
                    # Proceed to cluster the first articles
                    for data in first_articles:
                        url_article, text_article = data
                        vect_rep = bag_of_words_rep.get_rep(text_article)
                        self._clustering_component_1.add_document(url_article,
                                                                  text_article,
                                                                  vect_rep)
                        self._clustering_component_2.add_document(url_article,
                                                                  text_article,
                                                                  vect_rep)
                        self._clustering_component_3.add_document(url_article,
                                                                  text_article,
                                                                  vect_rep)
                        self._clustering_component_4.add_document(url_article,
                                                                  text_article,
                                                                  vect_rep)
                        self._clustering_component_5.add_document(url_article,
                                                                  text_article,
                                                                  vect_rep)

                    first_articles_processed = True

                vect_rep = bag_of_words_rep.get_rep(text)
                self._clustering_component_1.add_document(url_news,
                                                          text,
                                                          vect_rep)
                self._clustering_component_2.add_document(url_news,
                                                          text,
                                                          vect_rep)
                self._clustering_component_3.add_document(url_news,
                                                          text,
                                                          vect_rep)
                self._clustering_component_4.add_document(url_news,
                                                          text,
                                                          vect_rep)
                self._clustering_component_5.add_document(url_news,
                                                          text,
                                                          vect_rep)

        # Check against Google News' clustering
        for key, google_cluster in clustered_news.items():
            # TODO: habrá un forma más eficiente de comprobar esto?
            print("\n###########################################################")
            for url, data in google_cluster.items():
                cluster_1 = self._clustering_component_1.\
                    get_cluster_from_news_url(url)

                print("\n--------------------------------------------------------")
                print("\nurl: " + url)
                print("\nlen(google_cluster): " + str(len(google_cluster)))
                print("\ncluster_1.get_cluster_id():" + str(cluster_1.get_cluster_id()) +
                      "cluster_1.get_size():" + str(cluster_1.get_size()))

                cluster_2 = self._clustering_component_2.\
                    get_cluster_from_news_url(url)

                print("\ncluster_2.get_cluster_id():" + str(cluster_2.get_cluster_id()) +
                      "cluster_2.get_size():" + str(cluster_2.get_size()))
                # Obtain the cluster
                cluster_3 = self._clustering_component_3.\
                    get_cluster_from_news_url(url)

                print("\ncluster_3.get_cluster_id():" + str(cluster_3.get_cluster_id()) +
                      "cluster_3.get_size():" + str(cluster_3.get_size()))

                cluster_4 = self._clustering_component_4.\
                    get_cluster_from_news_url(url)

                print("\ncluster_4.get_cluster_id():" + str(cluster_4.get_cluster_id()) +
                      "cluster_4.get_size():" + str(cluster_4.get_size()))

                cluster_5 = self._clustering_component_5.\
                    get_cluster_from_news_url(url)

                print("\nid(cluster_5.get_cluster_id()):" + str(cluster_5.get_cluster_id()) +
                      "cluster_5.get_size():" + str(cluster_5.get_size()))

    # TODO: try this test after improving the implementation of the clustering
    # algorithm.
    def tesat_against_google_news_with_threads(self):
        corpus_file = open("news.data", "rb")
        clustered_news = pickle.load(corpus_file)
        news = pickle.load(corpus_file)

        glob_index_file_name = "globIndexTest"
        # Prepare an empty global index
        glob_index_file = open(glob_index_file_name, "wb")
        # {Word x frequency in the whole collection}
        pickle.dump({}, glob_index_file)
        # Collection size
        pickle.dump(0, glob_index_file)
        # Amount of words into the collection
        pickle.dump(0, glob_index_file)
        # {Word x position of the word (dimension) into the sparse vector that
        # represents each document}
        pickle.dump({}, glob_index_file)
        glob_index_file.close()

        articles_queue = Queue()
        vect_rep_queue = Queue()
        sentinel_value = ""
        threaded_bag_of_words_rep = ThreadedBagOfWordsRep(articles_queue,
                                                          vect_rep_queue,
                                                          glob_index_file_name,
                                                          sentinel_value)

        threaded_bag_of_words_rep.start()

        threaded_kmeans_clustering_component = \
            ThreadedKMeansClusteringComponent(vect_rep_queue,
                                              tests_file,
                                              sentinel_value)

        threaded_kmeans_clustering_component.start()
        articles_sent = 1
        for url_news, data in news.items():
            sys.stdout.write("\rTests - articles sent:%d" % articles_sent)
            sys.stdout.flush()
            cluster_id, title, body = data
            articles_queue.put((url_news, title, body))

        # Last element
        articles_queue.put((sentinel_value, sentinel_value, sentinel_value))

        # Wait threads to finalize
        while threaded_kmeans_clustering_component.is_alive() or\
                threaded_bag_of_words_rep.is_alive():

            time.sleep(10)

        assert(False)
        # Check against Google News' clustering
        self.assertEqual(len(clustered_news),
        threaded_kmeans_clustering_component._clustering_component.get_clusters_quantity())

    def test_cosine_similarity(self):
        # Different vectors
        v_1 = VectRep(2)
        v_1[0] = 0.0
        v_1[1] = 2.0
        v_1.set_length(2.0)

        v_2 = VectRep(2)
        v_2[0] = 1.0
        v_2[1] = 2.0
        v_2.set_length(sqrt(5))

        distance = self._clustering_component_1._cosine_similarity(v_1, v_2)

        correct_distance = (0.0 * 1.0 + 2.0 * 2.0) / (v_1.get_length() *
                                                      v_2.get_length())

        self.assertAlmostEqual(correct_distance, distance)

        # Different, and in particular, orthogonal vectors
        v_2[0] = 2.0
        v_2[1] = 0.0
        v_1.set_length(2.0)
        distance = self._clustering_component_1._cosine_similarity(v_1, v_2)

        self.assertAlmostEqual(0.0, distance)

        # Same vector
        distance = self._clustering_component_1._cosine_similarity(v_1, v_1)

        self.assertAlmostEqual(distance, 1.0)
