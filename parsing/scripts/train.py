"""Train a parser.

Usage:
  train.py [-m <model>] [-k <value>] -o <file>
  train.py -h | --help

Options:
  -m <model>    Model to use [default: flat]:
                  flat: Flat trees
                  rbranch: Right branching trees
                  upcfg: Unlexicalized PCFG
  -k <value>    Use horizontal markovization (only for UPCFG).
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from corpus.ancora import SimpleAncoraCorpusReader

from parsing.baselines import Flat, RBranch
from parsing.upcfg import UPCFG

models = {
    'flat': Flat,
    'rbranch': RBranch,
    'upcfg': UPCFG
}

if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading corpus...')
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)

    print('Training model...')
    res = list(corpus.parsed_sents())
    train_len = int(len(res) * 0.9)
    # Train only over the first 90% of the corpus.
    parsed_sents = res[: train_len]
    m = str(opts['-m'])
    if m == 'upcfg':
        hm = opts['-k']
        if hm is not None:
            hm = int(hm)
        model = models[m](parsed_sents, horzMarkov=hm)
    else:
        model = models[m](parsed_sents)

    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
