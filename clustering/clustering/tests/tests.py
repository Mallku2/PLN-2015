# -*- coding: utf-8 -*-
from unittest import TestCase
from scipy.sparse import dok_matrix
from math import sqrt
from clustering_component import KMeansClusteringComponent, Cluster


class TestClustering(TestCase):

    def setUp(self):
        self._clustering_component = KMeansClusteringComponent("data_tests")

    def test_calculate_new_centroid(self):
        # TODO: terminar de escribir test mas interesantes
        # Cluster with one document
        vec_1 = dok_matrix((1, 2))
        vec_1[0, 0] = 0
        vec_1[0, 1] = 0
        cluster = Cluster("", vec_1, 0, id(vec_1))
        cluster._update_centroid()
        centroid = cluster.get_centroid()

        self.assertEqual(centroid.get_vec_rep_length(), 0)
        result = (centroid.get_vec_rep() - vec_1)
        col, rows = result.nonzero()
        self.assertEqual(len(col), 0)

        # Add a new document
        vec_2 = dok_matrix((1, 2))
        vec_2[0, 0] = 1
        vec_2[0, 1] = 1
        cluster.add_document("", vec_2, sqrt(2))
        cluster._update_centroid()
        centroid = cluster.get_centroid()

        # Check length
        correct_l = sqrt(pow((0 + 1) / 2.0, 2) + pow((0 + 1) / 2.0, 2))
        self.assertAlmostEqual(centroid.get_vec_rep_length(), correct_l)

        # Check centroid
        vec_3 = dok_matrix((1, 2))
        vec_3[0, 0] = (0 + 1) / 2.0
        vec_3[0, 1] = (0 + 1) / 2.0
        result = (centroid.get_vec_rep() - vec_3)
        col, rows = result.nonzero()
        self.assertEqual(len(col), 0)

    def test_add_vectors(self):
        # TODO: como ya tengo otro test hecho para saber si calculo bien el
        # centroide, aca solo me deberia concentrar en ver si estoy escogiendo
        # adecuadamente el cluster en donde ubico un nuevo documento.
        vector_1 = dok_matrix((1, 2))
        vector_1[0, 0] = 0
        vector_1[0, 1] = 2
        self._clustering_component.add_document("", vector_1, 2.0)
        clusters = self._clustering_component.get_clusters()

        # There is just one cluster...
        self.assertEqual(clusters.get_length(), 1)

        # That cluster has length 1, and vector_1 is in the cluster...
        for cluster in clusters:
            self.assertEqual(cluster.get_size(), 1)
            self.assertEqual(cluster.is_in_cluster(vector_1), True)

        # Add a new vector, which is close enough to conform a cluster with
        # the previous vector.
        vector_2 = dok_matrix((1, 2))
        vector_2[0, 0] = 0
        vector_2[0, 1] = 2

        self._clustering_component.add_document("", vector_2, 2.0)
        self.assertEqual(clusters.get_length(), 1)

        # That one cluster has length 2, and vector_2 is in the cluster...
        for cluster in clusters:
            self.assertEqual(cluster.get_size(), 2)
            self.assertEqual(cluster.is_in_cluster(vector_1), True)
            self.assertEqual(cluster.is_in_cluster(vector_2), True)

        # Add a vector that is orthogonal to the previous ones
        vector_3 = dok_matrix((1, 2))
        vector_3[0, 0] = 2
        vector_3[0, 1] = 0

        self._clustering_component.add_document("", vector_3, 2.0)
        self.assertEqual(self._clustering_component.get_clusters_quantity(), 2)

        for cluster in clusters:
            cluster_size = cluster.get_size()
            if cluster_size == 1:
                # Then, vector_3 must be its unique member...
                self.assertEqual(cluster.is_in_cluster(vector_3), True)
            else:
                # {cluster_size != 1}
                self.assertEqual(cluster_size, 2)
                self.assertEqual(cluster.is_in_cluster(vector_1), True)
                self.assertEqual(cluster.is_in_cluster(vector_2), True)

    def test_cosine_similarity(self):
        # Different vectors
        v_1 = dok_matrix((1, 2))
        v_1[0, 0] = 0.0
        v_1[0, 1] = 2.0
        l_v_1 = 2.0

        v_2 = dok_matrix((1, 2))
        v_2[0, 0] = 1.0
        v_2[0, 1] = 2.0
        l_v_2 = sqrt(5)

        distance = self._clustering_component._cosine_similarity(v_1, l_v_1,
                                                                 v_2, l_v_2)

        correct_distance = (0.0 * 1.0 + 2.0 * 2.0) / (l_v_1 * l_v_2)

        self.assertAlmostEqual(correct_distance, distance)

        # Different, and in particular, orthogonal vectors
        v_2[0, 0] = 2.0
        v_2[0, 1] = 0.0
        distance = self._clustering_component._cosine_similarity(v_1, l_v_1,
                                                                 v_2, 2.0)

        self.assertAlmostEqual(0.0, distance)

        # Same vector
        distance = self._clustering_component._cosine_similarity(v_1, l_v_1,
                                                                 v_1, l_v_1)

        self.assertAlmostEqual(distance, 1.0)
