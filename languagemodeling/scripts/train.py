"""Train an n-gram model.

Usage:
  train.py -n <n> -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from nltk.corpus import PlaintextCorpusReader

#from languagemodeling.ngram import NGram
from ngram import NGram

if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    
    # TODO: al final tenemos que poder extraer las sentencias del corpus. Este
    # es el codigo anterior: sents = gutenberg.sents('austen-emma.txt')
    
    my_corpus = PlaintextCorpusReader('./', ["Corpus Clarke"])
    sents = my_corpus.sents()
#     str = ""
#     for word in my_corpus.words():
#         str += "/" + word
#     corpus_tokenizado = open("corpus_tokenizado", "a")    
#     corpus_tokenizado.write(str)
#     corpus_tokenizado.close()
    
    # train the model
    n = int(opts['-n'])
    model = NGram(n, sents)
# 
#     # save it
#     filename = opts['-o']
#     f = open(filename, 'wb')
#     pickle.dump(model, f)
#     f.close()
