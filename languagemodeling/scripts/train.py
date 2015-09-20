"""Train an n-gram model.

Usage:
  train.py -n <n> [-m <model>] -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -m <model>    Model to use [default: ngram]:
                  ngram: Unsmoothed n-grams.
                  addone: N-grams with add-one smoothing.
                  interpolated: N-grams with linear interpolation smoothing.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""

from docopt import docopt
import pickle

from nltk.corpus.reader import PlaintextCorpusReader
from nltk.tokenize import RegexpTokenizer

# TODO: solucion temporal...
import sys
sys.path = sys.path + ["../../"]

from languagemodeling.ngram import NGram,AddOneNGram, InterpolatedNGram


if __name__ == '__main__':
    opts = docopt(__doc__)
    # Define a tokenizer suited for our corpus.
    # TODO: con este patron resolvemos la tokenizacion errada de nombres como
    # Moon-Watcher. También ayudamos a tokenizar bien el nombre Arthur C. Clarke.
    # ¿Es necesario hacer lo mismo con otros nombres?
    pattern = r'''(?ix)    # set flag to allow verbose regexps
                  (Arthur\sC\.\sClarke)
                | ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
                | \w+(-\w+)*        # words with optional internal hyphens
                | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
                | \.\.\.            # ellipsis
                | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
                '''
    tokenizer = RegexpTokenizer(pattern)

    # load the data
    # TODO: para entrenar nuestro modelo sobre el corpus de entrenamiento,
    # estoy teniendo que cambiar aqui el nombre del archivo con el corpus.
    sents = PlaintextCorpusReader("./", "Corpus Clarke Training", word_tokenizer=tokenizer).sents()
    
    # train the model
    n = int(opts['-n'])
    m = str(opts['-m'])
    model = None
    
    if m == "addone":
        model = AddOneNGram(n, sents)
    elif m == "ngram":
        model = NGram(n, sents)
    elif m == "interpolated":
        # TODO: agregar los restantes comandos para aceptar un valor de gamma
        # y la bandera addone
        model = InterpolatedNGram(n, sents, gamma=None, addone=True)
    else:
        print(__doc__)
    
    if model:
        # save it
        filename = opts['-o']
        f = open(filename, 'wb')
        pickle.dump(model, f)
        f.close()
