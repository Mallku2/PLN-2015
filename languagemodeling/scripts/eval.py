"""Evaluate a language model using the test set.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Language model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from nltk.corpus.reader import PlaintextCorpusReader

# TODO: solucion temporal...
import sys
sys.path = sys.path + ["../../"]

from corpus_clarke import corpus_clarke_tokenizer, corpus_clarke_tests_name

if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the model
    model_filename = str(opts['-i'])
    model_file = open(model_filename, 'rb')
    lang_model = pickle.load(model_file)
    model_file.close()
    sents = PlaintextCorpusReader("./", corpus_clarke_tests_name,
                                  word_tokenizer=corpus_clarke_tokenizer).\
        sents()

    # Compute M.
    m = 0
    for sent in sents:
        m += len(sent)

    c_entr = lang_model.cross_entropy(sents, m)

    p = lang_model.perplexity(c_entr)

    print("Cross entropy: "+str(c_entr))
    print("Perplexity: "+str(p))
