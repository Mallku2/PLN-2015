# https://docs.python.org/3/library/unittest.html
# TODO: le tuve que agregar la importacion de main, y el codigo del final
from unittest import TestCase, main

#from languagemodeling.ngram import NGram
from ngram import NGram


class TestNGram(TestCase):

    def setUp(self):
        self.sents = [
            'el gato come pescado .'.split(),
            'la gata come salmón .'.split(),
        ]

    def test_init_1gram(self):
        ngram = NGram(1, self.sents)

        counts = {
            (): 10,
            ('el',): 1,
            ('gato',): 1,
            ('come',): 2,
            ('pescado',): 1,
            ('.',): 2,
            ('la',): 1,
            ('gata',): 1,
            ('salmón',): 1,
        }
        print("ngram.counts:")
        print(dict(ngram.counts))
        self.assertEqual(dict(ngram.counts), counts)

    def test_init_2gram(self):
        ngram = NGram(2, self.sents)

        counts = {
            ('el',): 1,
            ('gato',): 1,
            ('come',): 2,
            ('pescado',): 1,
            # ('.',): 2,
            ('la',): 1,
            ('gata',): 1,
            ('salmón',): 1,
            ('el', 'gato'): 1,
            ('gato', 'come'): 1,
            ('come', 'pescado'): 1,
            ('pescado', '.'): 1,
            ('la', 'gata'): 1,
            ('gata', 'come'): 1,
            ('come', 'salmón'): 1,
            ('salmón', '.'): 1,
        }

        self.assertEqual(dict(ngram.counts), counts)

    def test_prob_1gram(self):
        ngram = NGram(1, self.sents)

        self.assertEqual(ngram.prob('pescado'), 0.1)
        self.assertEqual(ngram.prob('come'), 0.2)

    def test_prob(self):
        ngram = NGram(2, self.sents)

        self.assertEqual(ngram.prob('pescado', ['come']), 0.5)
        self.assertEqual(ngram.prob('salmón', ['come']), 0.5)
        
if __name__ == '__main__':
    main()

