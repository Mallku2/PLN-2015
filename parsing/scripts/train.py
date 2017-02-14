"""Train a parser.

Usage:
  train.py [-m <model>] [-k <value>] [-u] -o <file>
  train.py -h | --help

Options:
  -m <model>    Model to use [default: flat]:
                  flat: Flat trees
                  rbranch: Right branching trees
                  lbranch: Left branching trees
                  upcfg: Unlexicalized PCFG
  -k <value>    Use horizontal markovization (only for UPCFG).
  -u            Makes the parser to handle unaries productions (only for UPCFG).
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
from corpus.ancora import SimpleAncoraCorpusReader

from parsing.baselines import Flat, RBranch, LBranch
from parsing.upcfg import UPCFG

models = {
    'flat': Flat,
    'rbranch': RBranch,
    'lbranch': LBranch,
    'upcfg': UPCFG
}

if __name__ == '__main__':
    opts = docopt(__doc__)
    print('Loading corpus...')
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)

    print('Training model...')
    parsed_sents = list(corpus.parsed_sents())
    m = str(opts['-m'])
    if m == 'upcfg':
        # Markovization
        hm = opts['-k']
        if hm is not None:
            hm = int(hm)

        # {opts['-u'] is boolean}
        model = models[m](parsed_sents, horzMarkov=hm, unary=opts['-u'])

    else:
        model = models[m](parsed_sents)

    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
