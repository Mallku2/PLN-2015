# -*- coding: utf-8 -*-
from unittest import TestCase
import pickle
from scipy.sparse import lil_matrix
from math import log
from os import remove

from feature_selection import BagOfWordsRep

test_file = "globIndexTests"


class TestBagOfWordsRep(TestCase):

    def setUp(self):
        glob_index = open(test_file, "wb")
        # Set an empty global index
        pickle.dump({}, glob_index)  # Words' freq
        pickle.dump(0, glob_index)  # Corpus size
        pickle.dump(0, glob_index)  # Words into corpus
        pickle.dump({}, glob_index)  # Words' dimensions
        glob_index.close()

        self._bag_of_words_rep = BagOfWordsRep("globIndexTests")
        self._test_texts = ["Ante la demora de una ambulancia, los chicos fueron\
                            trasladados en forma particular hasta el Hospital \
                            Alberdi, durante la tarde.",
                            "Se esperan tormentas durante la tarde."]

    def tearDown(self):
        remove(test_file)

    def test_prepare_text(self):
        ret = self._bag_of_words_rep._prepare_text(self._test_texts[0])

        # TODO: esto esta bien?
        self.assertEqual(["demor",
                          "ambul",
                          "chic",
                          "traslad",
                          "form",
                          "particul",
                          "hospital",
                          "alberdi",
                          "durant",
                          "tard"], ret)

        ret = self._bag_of_words_rep._prepare_text(self._test_texts[1])

        # TODO: esto esta bien?
        self.assertEqual(["esper",
                          "torment",
                          "durant",
                          "tard"], ret)

    def test_update_global_index(self):
        # Word: "hospital"
        self._bag_of_words_rep._update_global_index("hospital", 10, 1)

        doc_freq = self._bag_of_words_rep.get_doc_freq()
        self.assertEqual({"hospital": 10}, doc_freq)

        corpus_size = self._bag_of_words_rep.get_corpus_size()
        self.assertEqual(1, corpus_size)

        words_into_corpus = self._bag_of_words_rep.get_words_into_corpus()
        self.assertEqual(1, words_into_corpus)

        words_dimensions = self._bag_of_words_rep.get_words_dimensions()
        self.assertEqual({"hospital": 0}, words_dimensions)

        # Word: "alberdi"
        self._bag_of_words_rep._update_global_index("alberdi", 5, 2)

        self.assertEqual({"hospital": 10.0, "alberdi": 5.0},
                         doc_freq)

        corpus_size = self._bag_of_words_rep.get_corpus_size()
        self.assertEqual(2, corpus_size)

        words_into_corpus = self._bag_of_words_rep.get_words_into_corpus()
        self.assertEqual(2, words_into_corpus)

        self.assertEqual({"hospital": 0, "alberdi": 1},
                         words_dimensions)

        # Word: "alberdi", again...
        self._bag_of_words_rep._update_global_index("alberdi", 5, 3)

        self.assertEqual({"hospital": 10.0, "alberdi": 10.0},
                         doc_freq)

        corpus_size = self._bag_of_words_rep.get_corpus_size()
        self.assertEqual(3, corpus_size)

        words_into_corpus = self._bag_of_words_rep.get_words_into_corpus()
        self.assertEqual(2, words_into_corpus)

        self.assertEqual({"hospital": 0, "alberdi": 1},
                         words_dimensions)

    def test_representation(self):
        waiting_first_articles = True
        rep = self._bag_of_words_rep.get_rep(self._test_texts[0],
                                             waiting_first_articles)

        # TODO: batch?
        # We are waiting for the first batch of articles. rep is None
        self.assertIsNone(rep)

        waiting_first_articles = False
        rep = self._bag_of_words_rep.get_rep(self._test_texts[1],
                                             waiting_first_articles)

        shape = (1, 12)

        self.assertEqual(rep.shape, shape)

        correct_rep = lil_matrix(shape)

        words_dimensions = self._bag_of_words_rep.get_words_dimensions()

        """ Stems: "demor",
                    "ambul",
                    "chic",
                    "traslad",
                    "form",
                    "particul",
                    "hospital",
                    "alberdi",
                    "durant",
                    "tard"
                    "esper",
                    "torment"
        """

        dim = words_dimensions["demor"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # demor

        dim = words_dimensions["ambul"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # ambul

        dim = words_dimensions["chic"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # chic

        dim = words_dimensions["traslad"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # traslad

        dim = words_dimensions["form"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # form

        dim = words_dimensions["particul"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # particul

        dim = words_dimensions["hospital"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # hospital

        dim = words_dimensions["alberdi"]
        correct_rep[0, dim] = log(0 + 1) * log(2.0 / (1 + 1))  # alberdi

        dim = words_dimensions["durant"]
        correct_rep[0, dim] = log(1 / 4.0 + 1) * log(2.0 / (2 + 1))  # durant

        dim = words_dimensions["tard"]
        correct_rep[0, dim] = log(1 / 4.0 + 1) * log(2.0 / (2 + 1))  # tard

        dim = words_dimensions["esper"]
        correct_rep[0, dim] = log(1 / 4.0 + 1) * log(2.0 / (1 + 1))  # esper

        dim = words_dimensions["torment"]
        correct_rep[0, dim] = log(1 / 4.0 + 1) * log(2.0 / (1 + 1))  # torment

        cols, rows = correct_rep.nonzero()
        pos_a = zip(cols, rows)

        cols, rows = rep.nonzero()
        pos_b = zip(cols, rows)

        for pos in pos_a:
            self.assertEqual(correct_rep[pos], rep[pos])
