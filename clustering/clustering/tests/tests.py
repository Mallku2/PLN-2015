# -*- coding: utf-8 -*-
from clustering.bag_of_words_rep.feature_selection import VectRep, \
                                                          BagOfWordsRep
import pickle
from unittest import TestCase
from math import sqrt
from clustering_component import KMeansClusteringComponent, Cluster

# TODO: debug
import pdb

tests_file = "data_tests"


class TestClustering(TestCase):

    def tearDown(self):
        f = open(tests_file, "w")
        f.truncate()
        f.close()

    def test_calculate_new_centroid(self):
        # Cluster with one document
        vec_1 = VectRep(2)
        vec_1[0] = 0
        vec_1[1] = 0
        vec_1.set_length(0)
        cluster = Cluster("", "", vec_1, id(vec_1), 1)
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

        # Add a new document, with dif. dimension
        vec_3 = VectRep(3)
        vec_3[0] = 0
        vec_3[1] = 0
        vec_3[2] = 1
        vec_3.set_length(1)
        cluster.add_document("", "", vec_3)
        centroid = cluster.get_centroid()

        # Check length
        correct_l = sqrt(pow((0 + 1 + 0) / 3.0, 2) + pow((0 + 1 + 0) / 3.0, 2)
                         + pow((0 + 0 + 1) / 3.0, 2))

        self.assertAlmostEqual(centroid.get_length(), correct_l)

        # Check centroid
        vec_4 = VectRep(3)
        vec_4[0] = (0 + 1 + 0) / 3.0
        vec_4[1] = (0 + 1 + 0) / 3.0
        vec_4[2] = (0 + 0 + 1) / 3.0
        self.assertTrue(vec_4.is_equal_to(centroid))

        # Add a new document, with dif. dimension
        vec_5 = VectRep(4)
        vec_5[0] = 1
        vec_5[1] = 0
        vec_5[2] = 0
        vec_5[3] = 0
        vec_5.set_length(1)
        cluster.add_document("", "", vec_5)
        centroid = cluster.get_centroid()

        # Check length
        correct_l = sqrt(pow((0 + 1 + 0 + 1) / 4.0, 2) +
                         pow((0 + 1 + 0 + 0) / 4.0, 2) +
                         pow((0 + 0 + 1 + 0) / 4.0, 2) +
                         pow((0 + 0 + 0 + 0) / 4.0, 2))
        self.assertAlmostEqual(centroid.get_length(), correct_l)

        # Check centroid
        vec_6 = VectRep(4)
        vec_6[0] = (0 + 1 + 0 + 1) / 4.0
        vec_6[1] = (0 + 1 + 0 + 0) / 4.0
        vec_6[2] = (0 + 0 + 1 + 0) / 4.0
        vec_6[3] = (0 + 0 + 0 + 0) / 4.0

        self.assertTrue(vec_6.is_equal_to(centroid))

    def test_add_vectors(self):
        vector_1 = VectRep(2)
        vector_1[0] = 0
        vector_1[1] = 2
        vector_1.set_length(2)
        cluster_component = KMeansClusteringComponent(tests_file, 0.2, 1)
        cluster_component.add_document("", "", vector_1)
        clusters = cluster_component.get_clusters()

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
        cluster_component.add_document("", "", vector_2)
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
        cluster_component.add_document("new_vector", "", vector_3)
        self.assertEqual(cluster_component.get_clusters_quantity(), 2)

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

    def test_against_google_news_original_centroid_def(self):
        self._test_against_google_news(1)

    def test_against_google_news_new_centroid_def(self):
        self._test_against_google_news(2)

    def _test_against_google_news(self, centroid_type):
        clustering_components = []
        centroid_descr = None

        for i in range(14):
            clustering_components.append(KMeansClusteringComponent(
                                                tests_file, 0.2 + 0.05*i,
                                                centroid_type))

        corpus_file = open("news.data", "rb")
        clustered_news = pickle.load(corpus_file)
        news = pickle.load(corpus_file)

        glob_index_file_name = "globIndexTest"
        # Prepare an empty global index
        glob_index_file = open(glob_index_file_name, "wb")
        # Clean file
        glob_index_file.truncate()
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

        # Superb demonstration of natural language generation...
        if centroid_type == 1:
            centroid_descr = "original"
        else:
            # {centroid_type == 2}
            centroid_descr = "new"

        print("Clustering " + str(len(news)) + " news, using "
              + centroid_descr + " centroid definition.")

        for url_news, data in news.items():
            cluster_id, title, body = data
            text = title + "\n" + body

            if articles_processed < 100:
                # Just update the global index
                bag_of_words_rep.update_global_index_with_text(text)
                articles_processed += 1
                first_articles.append((url_news, text))
            else:
                # {articles_processed >= 100}

                articles_processed += 1
                print("articles_processed: " + str(articles_processed))
                if not first_articles_processed:
                    # Proceed to cluster the first articles
                    for url_article, text_article in first_articles:
                        vect_rep = bag_of_words_rep.get_rep(text_article)

                        for clust_comp in clustering_components:
                            clust_comp.add_document(url_article, text_article,
                                                    vect_rep)

                    first_articles_processed = True

                # {first_articles_processed}

                vect_rep = bag_of_words_rep.get_rep(text)

                for clust_comp in clustering_components:
                    clust_comp.add_document(url_news, text, vect_rep)

        # Create centroids for the Google News corpus
        google_clusters_centroids = {}
        for key, google_cluster in clustered_news.items():
            cluster_object = None
            for url, data in google_cluster.items():
                title, body = data
                text = title + "\n" + body
                vect_rep = bag_of_words_rep.get_rep(text)

                if not cluster_object:
                    cluster_object = Cluster(url, text, vect_rep, key,
                                             centroid_type)
                else:
                    # {cluster_object}
                    cluster_object.add_document(url, text, vect_rep)

            google_clusters_centroids[key] = cluster_object

        # Compare with our clustering
        for i in range(len(clustering_components)):
            clus_comp = clustering_components[i]
            print("\n########################################################")
            print("\nthreshold: " + str(clus_comp.get_clustering_threshold()))
            precission = 0.0
            recall = 0.0
            for key, google_clust_obj in google_clusters_centroids.items():
                # Search the cluster in clus_comp which is similar to
                # cluster_object
                max_cos_sim = float("-inf")
                nrst_cluster = None

                for cluster in clus_comp.get_clusters():
                    cos_sim = cluster.get_centroid().\
                        cosine_similarity(google_clust_obj.get_centroid())

                    if cos_sim > max_cos_sim:
                        max_cos_sim = cos_sim
                        nrst_cluster = cluster

                hits = 0.0
                for document in google_clust_obj:
                    url = document.get_url()
                    if nrst_cluster.is_in_cluster_by_url(url):
                        hits += 1.0

                precission += hits / nrst_cluster.get_size()
                recall += hits / google_clust_obj.get_size()

            precission /= len(google_clusters_centroids)
            recall /= len(google_clusters_centroids)
            print("Precission: " + str(precission))
            print("Recall: " + str(recall))
            print("F-Measure: " + str(2 * precission * recall /
                                      (precission + recall)))
        pdb.set_trace()

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

        distance = v_1.cosine_similarity(v_2)

        correct_distance = (0.0 * 1.0 + 2.0 * 2.0) / (v_1.get_length() *
                                                      v_2.get_length())

        self.assertAlmostEqual(correct_distance, distance)

        # Different, and in particular, orthogonal vectors
        v_2[0] = 2.0
        v_2[1] = 0.0
        v_1.set_length(2.0)
        distance = v_1.cosine_similarity(v_2)

        self.assertAlmostEqual(0.0, distance)

        # Same vector
        distance = v_1.cosine_similarity(v_1)

        self.assertAlmostEqual(distance, 1.0)
