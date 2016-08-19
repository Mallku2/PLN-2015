# -*- coding: utf-8 -*-
from unittest import TestCase
from scipy.sparse import dok_matrix
from math import sqrt
from clustering_component import KMeansClusteringComponent


class TestClustering(TestCase):

    def setUp(self):
        self._clustering_component = KMeansClusteringComponent()

    def test_add_vectors(self):
        vector_1 = dok_matrix((1, 2))
        vector_1[0, 0] = 0
        vector_1[0, 1] = 2
        l_vector_1 = sqrt(5)
        self._clustering_component.add_and_cluster_new_document(vector_1)
        documents = self._clustering_component.get_documents()

        # There is just one cluster...
        self.assertEqual(len(documents), 1)

        # And vector_1 is the centroid of the cluster...
        for k in documents:
            centroid, length = documents[k][0]
            result = (centroid - vector_1)
            col, rows = result.nonzero()
            self.assertEqual(len(col), 0)

        # Add a new vector, which is close enough to conform a cluster with
        # the previous vector.
        vector_2 = dok_matrix((1, 2))
        vector_2[0, 0] = 0
        vector_2[0, 1] = 2

        self._clustering_component.add_and_cluster_new_document(vector_2)
        self.assertEqual(len(documents), 1)

        # Add a vector that is orthogonal to the previous ones
        vector_3 = dok_matrix((1, 2))
        vector_3[0, 0] = 2
        vector_3[0, 1] = 0

        self._clustering_component.add_and_cluster_new_document(vector_3)
        self.assertEqual(len(documents), 2)

        # And vector_3 is the centroid of the cluster...
        vect_3_is_centroid = False
        for k in documents:
            centroid, length = documents[k][0]
            result = (centroid - vector_3)
            col, rows = result.nonzero()
            vect_3_is_centroid = (vect_3_is_centroid or len(col) == 0)

        self.assertEqual(vect_3_is_centroid, True)

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

        # Different and, in particular, orthogonal vectors
        v_2[0, 0] = 2.0
        v_2[0, 1] = 0.0
        distance = self._clustering_component._cosine_similarity(v_1, l_v_1,
                                                                 v_2, 2.0)

        self.assertAlmostEqual(0.0, distance)

        # Same vector
        distance = self._clustering_component._cosine_similarity(v_1, l_v_1,
                                                                 v_1, l_v_1)

        self.assertAlmostEqual(distance, 1.0)
