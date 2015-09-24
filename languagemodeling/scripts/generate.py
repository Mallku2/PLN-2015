"""Generate natural language sentences using a language model.

Usage:
  generate.py -i <file> -n <n>
  generate.py -h | --help

Options:
  -i <file>     Language model file.
  -n <n>        Number of sentences to generate.
  -h --help     Show this screen.
"""

from docopt import docopt
import pickle

# TODO: solucion temporal...
import sys
sys.path = sys.path + ["../../"]

from languagemodeling.ngram import NGramGenerator


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the model
    model_filename = str(opts['-i'])
    model_file = open(model_filename, 'rb')
    lang_model = pickle.load(model_file)
    model_file.close()

    # generate sentences
    n = int(opts['-n'])
    ngram_generator = NGramGenerator(lang_model)
    for i in range(n):
        sent = ""
        for word in ngram_generator.generate_sent():
            sent += word + " "

        print(sent+"\n\n")
