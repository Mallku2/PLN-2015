"""Evaulate a tagger.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Tagging model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
import sys

from sklearn.metrics import confusion_matrix
from corpus.ancora import SimpleAncoraCorpusReader


def progress(msg, width=None):
    """Output the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the model
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    # load the data
    files = '3LB-CAST/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    sents = list(corpus.tagged_sents())

    # tag
    hits, total = 0, 0
    u_wds_hits_total, k_wds_hits_total = 0, 0
    total_u_wds, total_k_wds = 0, 0
    n = len(sents)
    y_test = []
    y_pred = []
    for i, sent in enumerate(sents):
        word_sent, gold_tag_sent = zip(*sent)
        y_test += gold_tag_sent
        model_tag_sent = model.tag(word_sent)
        y_pred += model_tag_sent
        assert len(model_tag_sent) == len(gold_tag_sent), i

        # global score
        hits_sent = [m == g for m, g in zip(model_tag_sent, gold_tag_sent)]

        # Positions in sent of unknown words.
        u_wds_pos = set(j for j in range(len(word_sent)) if
                        model.unknown(word_sent[j]))
        # Positions in sent of known words.
        k_wds_pos = set(j for j in range(len(word_sent)) if j not in
                        u_wds_pos)

        u_wds_hits = [model_tag_sent[j] == gold_tag_sent[j] for j in
                      u_wds_pos]

        k_wds_hits = [model_tag_sent[j] == gold_tag_sent[j] for j in
                      k_wds_pos]

        hits += sum(hits_sent)
        u_wds_hits_total += sum(u_wds_hits)
        k_wds_hits_total += sum(k_wds_hits)
        total_u_wds += len(u_wds_pos)
        total_k_wds += len(k_wds_pos)
        total += len(sent)
        acc = float(hits) / total

        progress('{:3.1f}% ({:2.2f}%)'.format(float(i) * 100 / n, acc * 100))

    acc = float(hits) / total
    acc_knwn = float("inf")
    acc_unknwn = float("inf")
    if total_k_wds > 0:
        acc_knwn = float(k_wds_hits_total) / total_k_wds
    if total_u_wds > 0:
        acc_unknwn = float(u_wds_hits_total) / total_u_wds

    # Show stats.
    print('')
    print('Accuracy: {:2.2f}%'.format(acc * 100))
    print('Accuracy over known words: {:2.2f}%'.format(acc_knwn * 100))
    print('Accuracy over unknown words: {:2.2f}%'.format(acc_unknwn * 100))

    # Confusion matrix.
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion matrix:")
    print(cm)
