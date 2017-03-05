# -*- coding: utf-8 -*-
from unittest import TestCase
from math import log
from os import remove
import pickle

from feature_selection import BagOfWordsRep, VectRep

test_file = "globIndexTests"


class TestBagOfWordsRep(TestCase):

    def setUp(self):
        glob_index = open(test_file, "wb")
        # Set an empty global index
        pickle.dump({}, glob_index)  # Words' freq
        pickle.dump(0, glob_index)  # collection size
        pickle.dump(0, glob_index)  # Words into collection
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

        self.assertEqual(["esper",
                          "torment",
                          "durant",
                          "tard"], ret)

    def test_update_global_index(self):
        # Word: "hospital"
        self._bag_of_words_rep._update_global_index_with_word("hospital", 1)
        self._bag_of_words_rep._update_global_index_with_word("hospital", 2)

        doc_freq = self._bag_of_words_rep.get_doc_freq()
        self.assertEqual({"hospital": 2}, doc_freq)

        collection_size = self._bag_of_words_rep.get_collection_size()
        self.assertEqual(2, collection_size)

        words_into_collection = self._bag_of_words_rep.\
            get_amount_words_into_collection()

        self.assertEqual(1, words_into_collection)

        words_dimensions = self._bag_of_words_rep.get_words_dimensions()
        self.assertEqual({"hospital": 0}, words_dimensions)

        # Word: "alberdi"
        self._bag_of_words_rep._update_global_index_with_word("alberdi", 2)

        self.assertEqual({"hospital": 2.0, "alberdi": 1.0},
                         doc_freq)

        collection_size = self._bag_of_words_rep.get_collection_size()
        self.assertEqual(2, collection_size)

        words_into_collection = self._bag_of_words_rep.\
            get_amount_words_into_collection()
        self.assertEqual(2, words_into_collection)

        self.assertEqual({"hospital": 0, "alberdi": 1},
                         words_dimensions)

        # Word: "alberdi", again...
        self._bag_of_words_rep._update_global_index_with_word("alberdi", 3)

        self.assertEqual({"hospital": 2.0, "alberdi": 2.0},
                         doc_freq)

        collection_size = self._bag_of_words_rep.get_collection_size()
        self.assertEqual(3, collection_size)

        words_into_collection = self._bag_of_words_rep.\
            get_amount_words_into_collection()

        self.assertEqual(2, words_into_collection)

        self.assertEqual({"hospital": 0, "alberdi": 1},
                         words_dimensions)

    def test_representation(self):
        rep = self._bag_of_words_rep.get_rep(self._test_texts[0])
        self.assertEqual(rep.get_dimensions(), 10)

        rep = self._bag_of_words_rep.get_rep(self._test_texts[1])

        self.assertEqual(rep.get_dimensions(), 12)

        correct_rep = VectRep(12)

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
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # demor

        dim = words_dimensions["ambul"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # ambul

        dim = words_dimensions["chic"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # chic

        dim = words_dimensions["traslad"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # traslad

        dim = words_dimensions["form"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # form

        dim = words_dimensions["particul"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # particul

        dim = words_dimensions["hospital"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # hospital

        dim = words_dimensions["alberdi"]
        correct_rep[dim] = log(0 + 1) * log(2.0 / (1 + 1))  # alberdi

        dim = words_dimensions["durant"]
        correct_rep[dim] = log(1 / 4.0 + 1) * log(2.0 / (2 + 1))  # durant

        dim = words_dimensions["tard"]
        correct_rep[dim] = log(1 / 4.0 + 1) * log(2.0 / (2 + 1))  # tard

        dim = words_dimensions["esper"]
        correct_rep[dim] = log(1 / 4.0 + 1) * log(2.0 / (1 + 1))  # esper

        dim = words_dimensions["torment"]
        correct_rep[dim] = log(1 / 4.0 + 1) * log(2.0 / (1 + 1))  # torment

        self.assertTrue(correct_rep.is_equal_to(rep))
