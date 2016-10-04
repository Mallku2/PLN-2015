# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from collections import defaultdict
from math import log2

from tagging.hmm import HMM


class TestHMM(TestCase):

    def test_tag_prob(self):
        tagset = {'D', 'N', 'V'}
        trans = {
            ('<s>', '<s>'): {'D': 1.0},
            ('<s>', 'D'): {'N': 1.0},
            ('D', 'N'): {'V': 1.0},
            ('N', 'V'): {'</s>': 1.0},
        }
        out = {
            'D': {'the': 1.0},
            'N': {'dog': 0.4, 'barks': 0.6},
            'V': {'dog': 0.1, 'barks': 0.9},
        }
        hmm = HMM(3, tagset, trans, out)

        y = 'D N V'.split()
        p = hmm.tag_prob(y)
        self.assertAlmostEqual(p, 1.0)

        lp = hmm.tag_log_prob(y)
        self.assertAlmostEqual(lp, log2(1.0))

    def test_prob(self):
        tagset = {'D', 'N', 'V'}
        trans = {
            ('<s>', '<s>'): {'D': 1.0},
            ('<s>', 'D'): {'N': 1.0},
            ('D', 'N'): {'V': 1.0},
            ('N', 'V'): {'</s>': 1.0},
        }
        out = defaultdict(float, {
            'D': {'the': 1.0},
            'N': {'dog': 0.4, 'barks': 0.6},
            'V': {'dog': 0.1, 'barks': 0.9},
        })
        hmm = HMM(3, tagset, trans, out)

        x = 'the dog barks'.split()
        y = 'D N V'.split()
        p = hmm.prob(x, y)
        self.assertAlmostEqual(p, 0.4 * 0.9)

        lp = hmm.log_prob(x, y)
        self.assertAlmostEqual(lp, log2(0.4 * 0.9))

    def test_tag_prob2(self):
        tagset = {'D', 'N', 'V'}
        trans = {
            ('<s>', '<s>'): {'D': 1.0},
            ('<s>', 'D'): {'N': 1.0},
            ('D', 'N'): {'V': 0.8, 'N': 0.2},
            ('N', 'N'): {'V': 1.0},
            ('N', 'V'): {'</s>': 1.0},
        }
        out = {
            'D': {'the': 1.0},
            'N': {'dog': 0.4, 'barks': 0.6},
            'V': {'dog': 0.1, 'barks': 0.9},
        }
        hmm = HMM(3, tagset, trans, out)

        y = 'D N V'.split()
        p = hmm.tag_prob(y)
        self.assertAlmostEqual(p, 0.8)

        lp = hmm.tag_log_prob(y)
        self.assertAlmostEqual(lp, log2(0.8))

    def test_prob2(self):
        tagset = {'D', 'N', 'V'}
        trans = {
            ('<s>', '<s>'): {'D': 1.0},
            ('<s>', 'D'): {'N': 1.0},
            ('D', 'N'): {'V': 0.8, 'N': 0.2},
            ('N', 'N'): {'V': 1.0},
            ('N', 'V'): {'</s>': 1.0},
        }
        out = defaultdict(float, {
            'D': {'the': 1.0},
            'N': {'dog': 0.4, 'barks': 0.6},
            'V': {'dog': 0.1, 'barks': 0.9},
        })
        hmm = HMM(3, tagset, trans, out)

        x = 'the dog barks'.split()
        y = 'D N V'.split()
        p = hmm.prob(x, y)
        self.assertAlmostEqual(p, 0.8 * 0.4 * 0.9)

        lp = hmm.log_prob(x, y)
        self.assertAlmostEqual(lp, log2(0.8 * 0.4 * 0.9))

    def test_prob_unigrams(self):
        tagset = {'D', 'N', 'V'}
        trans = {
            (): {'D': 0.25, 'N': 0.25, 'V': 0.25, '</s>': 0.25}
        }
        out = defaultdict(float, {
            'D': {'the': 1.0},
            'N': {'dog': 0.4, 'barks': 0.6},
            'V': {'dog': 0.1, 'barks': 0.9},
        })
        hmm = HMM(1, tagset, trans, out)

        x = 'the dog barks'.split()
        y = 'D N V'.split()
        p = hmm.prob(x, y)
        correct_out_prob = 1.0 * 0.4 * 0.9
        correct_tag_prob = pow(0.25, 4)
        self.assertAlmostEqual(p,  correct_tag_prob * correct_out_prob)

        lp = hmm.log_prob(x, y)
        self.assertAlmostEqual(lp,
                               log2(correct_tag_prob) + log2(correct_out_prob))

    def test_prob_bigrams(self):
        tagset = {'D', 'N', 'V'}
        trans = {
            ('<s>',): {'D': 1.0},
            ('D',): {'N': 1.0},
            ('N',): {'V': 0.8, 'N': 0.2},
            ('V',): {'</s>': 1.0},
        }
        out = defaultdict(float, {
            'D': {'the': 1.0},
            'N': {'dog': 0.4, 'barks': 0.6},
            'V': {'dog': 0.1, 'barks': 0.9},
        })
        hmm = HMM(2, tagset, trans, out)

        x = 'the dog barks'.split()
        y = 'D N V'.split()
        p = hmm.prob(x, y)
        tag_prob = hmm.tag_prob(y)
        correct_out_prob = 1.0 * 0.4 * 0.9
        correct_tag_prob = 1.0 * 1.0 * 0.8 * 1.0
        self.assertAlmostEqual(p, correct_tag_prob * correct_out_prob)

        lp = hmm.log_prob(x, y)
        self.assertAlmostEqual(lp,
                               log2(correct_tag_prob) + log2(correct_out_prob))
