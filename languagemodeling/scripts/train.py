"""Train an n-gram model.

Usage:
  train.py -n <n> [-m <model>] -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -m <model>    Model to use [default: ngram]:
                  ngram: Unsmoothed n-grams.
                  addone: N-grams with add-one smoothing.
                  interpolation: N-grams with linear interpolation smoothing.
                  backoff: N-grams with Back-Off with discounting smoothing.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""

from docopt import docopt
import pickle

from nltk.corpus.reader import PlaintextCorpusReader

# TODO: solucion temporal...
import sys
sys.path = sys.path + ["../../"]

from languagemodeling.ngram import NGram, AddOneNGram, InterpolatedNGram, \
    BackOffNGram
from corpus_clarke import corpus_clarke_tokenizer, corpus_clarke_name

if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    sents = PlaintextCorpusReader("./", corpus_clarke_name,
                                  word_tokenizer=corpus_clarke_tokenizer).\
        sents()
    # train the model
    n = int(opts['-n'])
    m = str(opts['-m'])
    model = None

    if m == "addone":
        model = AddOneNGram(n, sents)
    elif m == "ngram":
        model = NGram(n, sents)
    elif m == "interpolation":
        model = InterpolatedNGram(n, sents, gamma=None, addone=True)
    elif m == "backoff":
        model = BackOffNGram(n, sents, beta=None, addone=True)
    else:
        print(__doc__)

    if model:
        # save it
        filename = opts['-o']
        f = open(filename, 'wb')
        pickle.dump(model, f)
        f.close()
