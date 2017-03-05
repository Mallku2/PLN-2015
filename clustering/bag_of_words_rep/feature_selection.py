# -*- coding: utf-8 -*-
from math import log, sqrt
from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from scipy.sparse import dok_matrix
import pickle


class VectRep(dok_matrix):

    def __init__(self, dimensions):
        dok_matrix.__init__(self, (1, dimensions))
        self._dimensions = dimensions
        self._length = None

    def nonzero(self):
        rows, cols = dok_matrix.nonzero(self)

        return cols

    def set_length(self, length):
        self._length = length

    def get_length(self):
        return self._length

    def get_dimensions(self):
        return self._dimensions

    def resize(self, new_dimensions):
        self._dimensions = new_dimensions
        dok_matrix.resize(self, (1, new_dimensions))

    def is_equal_to(self, another_vect):
        ret = self.get_dimensions() == another_vect.get_dimensions()

        if ret:
            result = (another_vect - self)
            # NOTE: we do this to avoid the redefinition of substraction...
            cols, rows = dok_matrix.nonzero(result)
            ret = len(cols) == 0

        return ret

    def cosine_similarity(self, vect):
        """Returns the cosine similarity between self and vect.
        PARAMS
        vect : instance of VecrRep."""

        l_vect = vect.get_length()

        assert(l_vect > 0.0)

        comp_product = 0

        # Get the positions of the non-zero entries of vect_1
        if self.get_dimensions() <= vect.get_dimensions():
            cols = self.nonzero()
        else:
            # {self.get_dimensions() > vect.get_dimensions()}
            cols = vect.nonzero()

        for pos in cols:
            comp_product += self[pos] * vect[pos]

        return comp_product / (self.get_length() * l_vect)

    def __getitem__(self, index):
        return dok_matrix.__getitem__(self, (0, index))

    def __setitem__(self, index, value):
        dok_matrix.__setitem__(self, (0, index), value)


class BagOfWordsRep:

    def __init__(self, glob_index_file_name):
        # Tokenizer
        pattern = r'''(?:[a-z]\.)+|\$?\d+(?:\.\d+)?%?|\w+(?:-\w+)*'''
        self._tokenizer = RegexpTokenizer(pattern)

        # Stemmer
        self._stemmer = SnowballStemmer("spanish")

        # Stop-words.
        stop_words_file = open("../bag_of_words_rep/stopWordsSerialized", "rb")
        self._stop_words_set = pickle.load(stop_words_file)
        stop_words_file.close()

        # Global index.
        self._glob_indx_file = open(glob_index_file_name, "r+b")
        # {Word x frequency in the whole collection}
        self._doc_freq = pickle.load(self._glob_indx_file)
        self._collection_size = pickle.load(self._glob_indx_file)
        self._amount_words_into_collection = pickle.load(self._glob_indx_file)
        # {Word x position of the word (dimension) into the sparse vector that
        # represents each document}
        self._words_dimensions = pickle.load(self._glob_indx_file)

    def _prepare_text(self, text):
        """Prepare the text for the construction of its vectorial representation.
        RETURNS
        TODO: non-stop-words?????
        a list representing a lower case, non-stop-words, tokenized version of
        the text received
        """
        # Tokenize.
        text_tokenized = self._tokenizer.tokenize(text)
        # Delete stop-words.
        text_without_stop_words = filter(lambda x: x.lower() not in
                                         self._stop_words_set, text_tokenized)

        # Reduce each word to its stem.
        text_stems = list(map(self._stemmer.stem, text_without_stop_words))

        return text_stems

    def get_rep(self, text):
        """Returns the vectorial representation of the received text, using the
        TF-IDF weighting.
        PARAMS
        text : A string. The text to be vectorized.

        RETURNS
        An instance of VectRep.
        """

        text_stems = self._prepare_text(text)
        l_text_stems = float(len(text_stems))

        stems_set = set(text_stems)

        rep = VectRep(self._amount_words_into_collection)

        new_collection_size = self._collection_size + 1
        summ = 0.0
        for stem in stems_set:
            raw_freq = text_stems.count(stem)

            # Update global index

            # TODO: si vamos a quedarnos con la nueva def de idf, no hace
            # falta pasar el valor de raw_freq
            new_word = self._update_global_index_with_word(stem,
                                                           new_collection_size)

            # Normalized raw term frequency within the document
            tf = log(raw_freq / l_text_stems + 1)

            idf = log(new_collection_size / float(self._doc_freq[stem] + 1))

            tf_idf = tf * idf

            # Save the tf.idf calculated, into the corresponding position.
            if new_word:
                rep.resize(self._amount_words_into_collection)

            rep[self._words_dimensions[stem]] = tf_idf
            summ += pow(tf_idf, 2.0)

        rep.set_length(sqrt(summ))

        return rep

    def update_global_index_with_text(self, text):
        text_stems = self._prepare_text(text)

        stems_set = set(text_stems)

        for stem in stems_set:
            # Update global index
            self._update_global_index_with_word(stem,
                                                self._collection_size + 1)

    def _update_global_index_with_word(self, word, new_collection_size):
        """Updates the global index:
            * the document frequency of the given word.
            * if the word is new, assigns to it a number that refers to the
            dimension that it represents in the vector space representation of
            a text.
            * sets the new collection size.

            PARAMS
            word: the stemmed version of a word.
            news_collection_size:

            RETURNS
            A boolean indicating if the word was already present in the global
            index.
        """

        new_word = False

        if word in self._doc_freq:
            self._doc_freq[word] += 1
        else:
            # {not word in self._doc_freq}
            self._doc_freq[word] = 1

            self._words_dimensions[word] = self._amount_words_into_collection
            self._amount_words_into_collection += 1
            new_word = True

        self._collection_size = new_collection_size

        return new_word

    def get_doc_freq(self):
        return self._doc_freq

    def get_collection_size(self):
        return self._collection_size

    def get_amount_words_into_collection(self):
        return self._amount_words_into_collection

    def get_words_dimensions(self):
        return self._words_dimensions

    def __del__(self):
        pickle.dump(self._doc_freq, self._glob_indx_file)
        pickle.dump(self._collection_size, self._glob_indx_file)
        pickle.dump(self._amount_words_into_collection, self._glob_indx_file)
        pickle.dump(self._words_dimensions, self._glob_indx_file)
        self._glob_indx_file.close()
