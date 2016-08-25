# -*- coding: utf-8 -*-
from math import log
# TODO: por ahora, utilizamos la implementación de nltk del algoritmo de
# stemming de Porter.
from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from scipy.sparse import dok_matrix
# TODO: cambie cPickle por pickle: primero, para hacer este código compatible
# con python3. Segundo, porque solo uso pickle en el constructor y el
# destructor (no hay, por lo tanto, necesidad de ser eficiente en esto).
import pickle
import pdb


class VectRep(dok_matrix):

    def __init__(self, dimensions):
        self._dimensions = dimensions
        dok_matrix.__init__(self, (1, dimensions))

    def get_vect_length(self):
        rows, cols = self.nonzero()
        summatory = sum([pow(self[pos], 2.0) for pos in zip(rows, cols)])
        """# TODO: esto se puede escribir en una sola linea
        for pos in zip(rows, cols):
            summatory += pow(self[pos], 2.0)"""

        # TODO: hace falta calcular sqrt?
        return sqrt(summatory)

    def get_dimensions(self):
        return self._dimensions

    def resize(self, new_dimensions):
        self._dimensions = new_dimensions
        dok_matrix.resize(self, (1, new_dimensions))

    def is_equal_to(self, another_vect):
        ret = self.get_dimensions() == another_vect.get_dimensions()

        if ret:
            result = (another_vect - self)
            col, rows = result.nonzero()
            ret = len(col) == 0

        return ret

    def __getitem__(self, index):
        return dok_matrix.__getitem__(self, (0, index))

    def __setitem__(self, index, value):
        return dok_matrix.__setitem__(self, (0, index), value)

class BagOfWordsRep:

    def __init__(self, glob_index_file):
        # Tokenizer
        # TODO: por alguna razón, usando esta primera versión del patrón, el
        # tokenizador no opera bien. Tenemos que agregarle el indicador
        # de "no captura" ?:
        """pattern = r'''(?ix)    # set flag to allow verbose regexps
                    | (?:[a-z]\.)+        # abbreviations, e.g. U.S.A.
                    | \$?\d+(?:\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
                    | \w+(?:-\w+)*        # words with optional internal hyphens
                    | \.\.\.            # ellipsis
                    | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
                '''
        """
        # TODO: estamos seguros de que no sería posible resolver el problema
        # simplemente intentando hacer encaje con los espacios vacios que deben
        # ser considerados como separación?, esto traería problemas con los nombres
        # propios (por ejemplo), pero eso altera nuestro tratamiento de la
        # semántica de los artículos?
        # TODO: actualmente, los signos de puntuación los descarto!
        pattern = r'''(?:[a-z]\.)+|\$?\d+(?:\.\d+)?%?|\w+(?:-\w+)*'''
        """
        pattern = r'''(?:[a-z]\.)+              # abbreviations, e.g. U.S.A.
                    |\$?\d+(?:\.\d+)?%?         # currency and percentages, e.g. $12.40, 82%
                    |\w+(?:-\w+)*               # words with optional internal hyphens
                    |\.\.\.                     # ellipsis
                    |[][.,;"'?():-_]  # these are separate tokens; includes ], [
                '''
        """
        self._tokenizer = RegexpTokenizer(pattern)

        # Stemmer
        self._stemmer = SnowballStemmer("spanish")

        # Stop-words.
        # TODO: estamos incrustando aquí la dirección de estos archivos...
        stop_words_file = open("../bag_of_words_rep/stopWordsSerialized", "rb")
        self._stop_words_set = pickle.load(stop_words_file)
        stop_words_file.close()

        # Global index.
        self._glob_indx_file = open(glob_index_file, "r+b")
        # {Word x frequency in the whole corpus}
        self._doc_freq = pickle.load(self._glob_indx_file)
        self._corpus_size = pickle.load(self._glob_indx_file)
        # TODO: no me gusta el nombre, y tampoco estoy seguro de que haga falta
        # mantenerlo en el archivo, ya que lo puedo calcular cada vez que
        # levando _doc_freq
        self._words_into_corpus = pickle.load(self._glob_indx_file)
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
        # TODO: posiblemente haga falta llevar todas las palabras a minúsculas,
        # porque mi lista de stop-words está en minúscula...
        text = text.lower()
        # Tokenize.
        text_tokenized = self._tokenizer.tokenize(text)
        # Delete stop-words.
        text_without_stop_words = filter(lambda x: x not in
                                         self._stop_words_set, text_tokenized)

        # Reduce each word to its stem.
        # TODO: revisar si el resultado es el correcto...no me diera la
        # impresión
        # de que eso es así...
        # TODO: buenas noticias!, el stemmer no acepta caracteres fuera de
        # ascii
        text_stems = list(map(self._stemmer.stem, text_without_stop_words))

        return text_stems

    def get_rep(self, text, waiting_first_articles):
        """Returns the vectorial representation of the received text, using the
        TF-IDF weighting.
        PARAMS
        text : A string. The text to be vectorized.

        waiting_first_articles : A boolean. Indicates if we are waiting for an
         initial determined amount of documents, before computing the TF-IDF
         weighting.

        RETURNS
        An instance of dok_matrix.
        """

        # TODO: cambiar el nombree de esta variable
        text_stems = self._prepare_text(text)
        l_text_stems = float(len(text_stems))

        stems_set = set(text_stems)

        rep = None
        if not waiting_first_articles:
            #rep = dok_matrix((1, self._words_into_corpus))
            rep = VectRep(self._words_into_corpus)
        else:
            # {waiting_first_articles}
            pass
            # TODO:?

        new_corpus_size = self._corpus_size + 1
        for stem in stems_set:
            raw_freq = text_stems.count(stem)

            # Update global index
            new_word = self._update_global_index(stem, raw_freq,
                                                 new_corpus_size)

            if not waiting_first_articles:
                tf = log(raw_freq / l_text_stems + 1)
                # TODO: esto está mal: ver
                # https://en.wikipedia.org/wiki/Tf%E2%80%93idf
                # IDF es la inversa de la frecuencia con la que un término
                # aparece en la colección de documentos!...
                # TODO: de acuerdo a https://www.youtube.com/watch?v=hXNbFNCgPfY
                # en tf se tiene en cuenta realmente la frecuencia: es decir,
                # se divide raw_freq por la cantidad de términos del documento
                # TODO: no queda claro si debo utiliza document frequency o
                # collection frequency. Voy a dejar implementado esto así,
                # y veré si con experimentación y/o nueva docu queda claro
                # como hacerlo.
                idf = log(new_corpus_size / float(self._doc_freq[stem] + 1))
                tf_idf = tf * idf

                # Save the tf.idf calculated, into the corresponding position.
                if new_word:
                    #rep.resize((1, self._words_into_corpus))
                    rep.resize(self._words_into_corpus)

                #rep[0, self._words_dimensions[stem]] = tf_idf
                rep[self._words_dimensions[stem]] = tf_idf

        return rep

    def _update_global_index(self, word, doc_count, new_corpus_size):
        """Updates the global index:
            * the document frequency of the given word.
            * if the word is new, assigns to it a number that refers to the
            dimension that it represents in the vector space representation of
            a text.
            * sets the new corpus size.

            PARAMS
            word: the stemmed version of a word.
            doc_count: the number of occurrences of the given word in the
            document being analyzed.
            news_corpus_size:

            RETURNS
            A boolean indicating if the word was already present in the global
            index.
        """

        # TODO: no deberíamos también actualizar la frecuencia de todas
        # las otras palabras?
        new_word = False

        if word in self._doc_freq:
            # TODO: De https://www.youtube.com/watch?v=a50Hv_N-yHA: "document
            # frequency"
            # es la cantidad de documentos que contienen a un término...se
            # considera que esta es medida es la inversa de la "información"
            # que posee un término, útil para considerarla en una consulta
            # (describe la inversa de qué tan informativo es un término). Este
            # estadístico es más útil en "information retrieval". Lo que se
            # debería utilizar aquí es "collection frequency" (cantidad de
            # veces que un término ha aparecido en los documentos), que
            # aparentemente es un estadístico más adecuado cuando se está
            # trabajando con la semántica de un lenguaje.
            self._doc_freq[word] += doc_count
        else:
            # {not word in self._doc_freq}
            self._doc_freq[word] = doc_count
            self._words_dimensions[word] = self._words_into_corpus
            self._words_into_corpus += 1
            new_word = True

        self._corpus_size = new_corpus_size

        return new_word

    def get_doc_freq(self):
        return self._doc_freq

    # TODO: no deberia ser algo como collection size?
    def get_corpus_size(self):
        return self._corpus_size

    def get_words_into_corpus(self):
        return self._words_into_corpus

    def get_words_dimensions(self):
        return self._words_dimensions

    def __del__(self):
        pickle.dump(self._doc_freq, self._glob_indx_file)
        pickle.dump(self._corpus_size, self._glob_indx_file)
        pickle.dump(self._words_into_corpus, self._glob_indx_file)
        pickle.dump(self._words_dimensions, self._glob_indx_file)
        self._glob_indx_file.close()

if __name__ == "__main__":
    obj = BagOfWordsRep()

    text = """Tras una hora y media de debate, el congreso del PJ concluyó poco
            antes de las 13 y decidió elegir una junta electoral con vistas a
            (los comicios internos del 8 de mayo) y U.S.A. $12 234234% para
            más adelante la modificación de la carta orgánica del partido."""
    print(str(obj.get_rep(text)))
