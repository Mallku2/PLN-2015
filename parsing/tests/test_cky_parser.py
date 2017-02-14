# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from math import log2

from nltk.tree import Tree
from nltk.grammar import PCFG

from parsing.cky_parser import CKYParser


class TestCKYParser(TestCase):

    def test_parse(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [1.0]
                NP -> Det Noun          [0.6]
                NP -> Noun Adj          [0.4]
                VP -> Verb NP           [1.0]
                Det -> 'el'             [1.0]
                Noun -> 'gato'          [0.9]
                Noun -> 'pescado'       [0.1]
                Verb -> 'come'          [1.0]
                Adj -> 'crudo'          [1.0]
            """)

        parser = CKYParser(grammar, False)

        lp, t = parser.parse('el gato come pescado crudo'.split())

        # check chart
        pi = {
            (1, 1): {'Det': log2(1.0)},
            (2, 2): {'Noun': log2(0.9)},
            (3, 3): {'Verb': log2(1.0)},
            (4, 4): {'Noun': log2(0.1)},
            (5, 5): {'Adj': log2(1.0)},

            (1, 2): {'NP': log2(0.6 * 1.0 * 0.9)},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': log2(0.4 * 0.1 * 1.0)},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S':
                     log2(1.0) +  # rule S -> NP VP
                     log2(0.6 * 1.0 * 0.9) +  # left part
                     log2(1.0) + log2(1.0) +
                     log2(0.4 * 0.1 * 1.0)},  # right part
        }
        self.assertEqualPi(parser._pi, pi)

        # check partial results
        bp = {
            (1, 1): {'Det': Tree.fromstring("(Det el)")},
            (2, 2): {'Noun': Tree.fromstring("(Noun gato)")},
            (3, 3): {'Verb': Tree.fromstring("(Verb come)")},
            (4, 4): {'Noun': Tree.fromstring("(Noun pescado)")},
            (5, 5): {'Adj': Tree.fromstring("(Adj crudo)")},

            (1, 2): {'NP': Tree.fromstring("(NP (Det el) (Noun gato))")},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': Tree.fromstring("(NP (Noun pescado) (Adj crudo))")},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': Tree.fromstring(
                "(VP (Verb come) (NP (Noun pescado) (Adj crudo)))")},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S': Tree.fromstring(
                """(S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                   )
                """)},
        }
        self.assertEqual(parser._bp, bp)

        # check tree
        t2 = Tree.fromstring(
            """
                (S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                )
            """)
        self.assertEqual(t, t2)

        # check log probability
        lp2 = log2(1.0 * 0.6 * 1.0 * 0.9 * 1.0 * 1.0 * 0.4 * 0.1 * 1.0)
        self.assertAlmostEqual(lp, lp2)

    def test_ambiguity(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [1.0]

                VP -> VP PP             [0.25]
                VP -> Vt NP             [0.25]
                VP -> V S               [0.25]
                VP -> 'duck'            [0.25]

                NP -> PRP NN            [0.5]
                NP -> Det Noun          [0.25]
                NP -> 'her'             [0.25]

                PP -> IN NP             [1.0]

                IN -> 'with'            [1.0]

                Det -> 'the'            [1.0]

                Noun -> 'girl'          [0.25]
                Noun -> 'telescope'     [0.75]

                Vt -> 'saw'             [1.0]

                PRP -> 'her'            [1.0]

                NN -> 'duck'            [1.0]
            """)

        parser = CKYParser(grammar, False)

        lp, t = parser.parse('the girl saw her duck with the telescope'
                             .split())

        # check tree
        t2 = Tree.fromstring("""
        (S
            (NP
                (Det the)
                (Noun girl))
            (VP
                (VP
                    (Vt saw)
                    (NP
                        (PRP her)
                        (NN duck)))
                (PP
                    (IN with)
                    (NP
                        (Det the)
                        (Noun telescope)))))
        """)
        self.assertEqual(t, t2)

        # check partial results
        bp = {(1, 1): {'Det': Tree('Det', ['the'])},
              (1, 2): {'NP': Tree('NP', [Tree('Det', ['the']),
                                         Tree('Noun', ['girl'])])},
              (1, 3): {},
              (1, 4): {'S': Tree('S', [Tree('NP', [Tree('Det', ['the']),
                                                   Tree('Noun', ['girl'])]),
                                       Tree('VP', [Tree('Vt', ['saw']),
                                                   Tree('NP', ['her'])])])},
              (1, 5): {'S': Tree('S', [Tree('NP', [Tree('Det', ['the']),
                                                   Tree('Noun', ['girl'])]),
                                       Tree('VP', [Tree('Vt', ['saw']),
                                                   Tree('NP', [Tree('PRP',
                                                               ['her']),
                                                               Tree('NN',
                                                               ['duck'])])
                                                   ])])},
              (1, 6): {},
              (1, 7): {},
              (1, 8): {'S': Tree('S',
                                 [Tree('NP',
                                  [Tree('Det', ['the']),
                                   Tree('Noun', ['girl'])]),
                                  Tree('VP',
                                  [Tree('VP',
                                        [Tree('Vt',
                                              ['saw']),
                                         Tree('NP',
                                              [Tree('PRP',
                                                    ['her']),
                                               Tree('NN',
                                                    ['duck'])])]),
                                   Tree('PP',
                                        [Tree('IN',
                                              ['with']),
                                         Tree('NP',
                                              [Tree('Det',
                                                    ['the']),
                                               Tree('Noun',
                                                    ['telescope'])])]
                                        )])])},
              (2, 2): {'Noun': Tree('Noun', ['girl'])},
              (2, 3): {},
              (2, 4): {},
              (2, 5): {},
              (2, 6): {},
              (2, 7): {},
              (2, 8): {},
              (3, 3): {'Vt': Tree('Vt', ['saw'])},
              (3, 4): {'VP': Tree('VP', [Tree('Vt', ['saw']),
                                         Tree('NP', ['her'])])},
              (3, 5): {'VP': Tree('VP', [Tree('Vt',
                                              ['saw']),
                                  Tree('NP',
                                       [Tree('PRP',
                                             ['her']),
                                        Tree('NN',
                                             ['duck'])])])},
              (3, 6): {},
              (3, 7): {},
              (3, 8): {'VP': Tree('VP',
                                   [Tree('VP',
                                    [Tree('Vt',
                                          ['saw']),
                                     Tree('NP',
                                          [Tree('PRP',
                                                ['her']),
                                           Tree('NN',
                                                ['duck'])])]),
                                    Tree('PP',
                                    [Tree('IN',
                                          ['with']),
                                     Tree('NP',
                                          [Tree('Det',
                                                ['the']),
                                           Tree('Noun',
                                                ['telescope'])])])])},
              (4, 4): {'NP': Tree('NP',
                                  ['her']),
                       'PRP': Tree('PRP',
                                   ['her'])},
              (4, 5): {'NP': Tree('NP',
                                  [Tree('PRP',
                                        ['her']),
                                   Tree('NN',
                                        ['duck'])]),
              'S': Tree('S',
                        [Tree('NP',
                              ['her']),
                         Tree('VP',
                              ['duck'])])},
              (4, 6): {},
              (4, 7): {},
              (4, 8): {'S': Tree('S',
                                 [Tree('NP',
                                       ['her']),
                                  Tree('VP',
                                       [Tree('VP',
                                             ['duck']),
                                        Tree('PP',
                                             [Tree('IN',
                                                   ['with']),
                                              Tree('NP',
                                                   [Tree('Det',
                                                         ['the']),
                                                    Tree('Noun',
                                                         ['telescope'])])])])])
                       },
              (5, 5): {'NN': Tree('NN', ['duck']), 'VP': Tree('VP', ['duck'])},
              (5, 6): {},
              (5, 7): {},
              (5, 8): {'VP': Tree('VP',
                                  [Tree('VP',
                                        ['duck']),
                                   Tree('PP',
                                        [Tree('IN',
                                              ['with']),
                                         Tree('NP',
                                              [Tree('Det',
                                                    ['the']),
                                               Tree('Noun',
                                                    ['telescope'])])])])},
              (6, 6): {'IN': Tree('IN',
                                  ['with'])},
              (6, 7): {},
              (6, 8): {'PP': Tree('PP',
                                  [Tree('IN',
                                        ['with']),
                                   Tree('NP',
                                        [Tree('Det',
                                              ['the']),
                                         Tree('Noun',
                                              ['telescope'])])])},
              (7, 7): {'Det': Tree('Det', ['the'])},
              (7, 8): {'NP': Tree('NP',
                                  [Tree('Det',
                                        ['the']),
                                   Tree('Noun',
                                        ['telescope'])])},
              (8, 8): {'Noun': Tree('Noun', ['telescope'])}}

        self.assertEqual(parser._bp, bp)

        pi = {(1, 1): {'Det': log2(1.0)},
              (1, 2): {'NP': log2(1.0) + log2(0.25) + log2(0.25)},
              (1, 3): {},
              (1, 4): {'S': log2(1.0) + log2(0.25) + log2(1) + log2(0.25) +
                       log2(0.25) + log2(1.0) + log2(0.25)},
              (1, 5): {'S': log2(1.0) + log2(0.25) + log2(1.0) + log2(0.25) +
                       log2(0.25) + log2(1.0) + log2(0.5) + log2(1.0) +
                       log2(1.0)},
              (1, 6): {},
              (1, 7): {},
              (1, 8): {'S': log2(1.0) + log2(0.25) + log2(1.0) + log2(0.25) +
                       log2(0.25) + log2(0.25) + log2(1.0) + log2(0.5) +
                       log2(1.0) + log2(1.0) + log2(1.0) + log2(1.0) +
                       log2(0.25) + log2(1.0) + log2(0.75)},
              (2, 2): {'Noun': log2(0.25)},
              (2, 3): {},
              (2, 4): {},
              (2, 5): {},
              (2, 6): {},
              (2, 7): {},
              (2, 8): {},
              (3, 3): {'Vt': log2(1.0)},
              (3, 4): {'VP': log2(0.25) + log2(1.0) + log2(0.25)},
              (3, 5): {'VP': log2(0.25) + log2(1.0) + log2(0.5) +
                       log2(1.0) + log2(1.0)},
              (3, 6): {},
              (3, 7): {},
              (3, 8): {'VP': log2(0.25) + log2(0.25) + log2(1.0) + log2(0.5) +
                       log2(1.0) + log2(1.0) + log2(1.0) + log2(1.0) +
                       log2(0.25) + log2(1.0) + log2(0.75)},
              (4, 4): {'NP': log2(0.25),
                       'PRP': log2(1.0)},
              (4, 5): {'NP': log2(0.5) + log2(1.0) + log2(1.0),
                       'S': log2(1.0) + log2(0.25) + log2(0.25)},
              (4, 6): {},
              (4, 7): {},
              (4, 8): {'S': log2(1.0) + log2(0.25) + log2(0.25) + log2(0.25) +
                       log2(1.0) + log2(1.0) + log2(0.25) + log2(1.0) +
                       log2(0.75)},
              (5, 5): {'NN': log2(1.0),
                       'VP': log2(0.25)},
              (5, 6): {},
              (5, 7): {},
              (5, 8): {'VP': log2(0.25) + log2(0.25) + log2(1.0) + log2(1.0) +
                       log2(0.25) + log2(1.0) + log2(0.75)},
              (6, 6): {'IN': log2(1.0)},
              (6, 7): {},
              (6, 8): {'PP': log2(1.0) + log2(1.0) + log2(0.25) + log2(1.0) +
                       log2(0.75)},
              (7, 7): {'Det': log2(1.0)},
              (7, 8): {'NP': log2(0.25) + log2(1.0) + log2(0.75)},
              (8, 8): {'Noun': log2(0.75)}}

        self.assertEqualPi(pi, parser._pi)

    def test_unaries(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [0.9]
                S -> VP                 [0.1]

                VP -> V NP              [0.5]
                VP -> V                 [0.1]
                VP -> V VP_V            [0.3]
                VP -> V PP              [0.1]

                VP_V -> NP PP           [1.0]

                NP -> NP NP             [0.1]
                NP -> NP PP             [0.2]
                NP -> N                 [0.7]

                PP -> P NP              [1.0]

                N -> 'people'           [0.5]
                N -> 'fish'             [0.2]
                N -> 'tanks'            [0.2]
                N -> 'rods'             [0.1]

                V -> 'people'           [0.1]
                V -> 'fish'             [0.6]
                V -> 'tanks'            [0.3]

                P -> 'with'             [1.0]
            """)

        parser = CKYParser(grammar, True)

        lp, t = parser.parse('fish people fish tanks'.split())

        pi = {(1, 1): {'N': log2(0.2),
                       'V': log2(0.6),
                       'NP': log2(0.2) + log2(0.7),
                       'VP': log2(0.6) + log2(0.1),
                       'S': log2(0.6) + log2(0.1) + log2(0.1)},

              (2, 2): {'N': log2(0.5),
                       'V': log2(0.1),
                       'NP': log2(0.5) + log2(0.7),
                       'VP': log2(0.1) + log2(0.1),
                       'S': log2(0.1) + log2(0.1) + log2(0.1)},

              (3, 3): {'N': log2(0.2),
                       'V': log2(0.6),
                       'NP': log2(0.2) + log2(0.7),
                       'VP': log2(0.6) + log2(0.1),
                       'S': log2(0.6) + log2(0.1) + log2(0.1)},

              (4, 4): {'N': log2(0.2),
                       'V': log2(0.3),
                       'NP': log2(0.2) + log2(0.7),
                       'VP': log2(0.3) + log2(0.1),
                       'S': log2(0.3) + log2(0.1) + log2(0.1)},

              (1, 2): {'NP': log2(0.0049),
                       'VP': log2(0.105),
                       'S': log2(0.105) + log2(0.1)
                       },

              (2, 3): {'NP': log2(0.35) + log2(0.14) + log2(0.1),
                       'VP': log2(0.1) + log2(0.14) + log2(0.5),
                       'S': log2(0.35) + log2(0.06) + log2(0.9)},

              (3, 4): {'NP': log2(0.14) + log2(0.14) + log2(0.1),
                       'VP': log2(0.6) + log2(0.14) + log2(0.5),
                       'S': log2(0.1) + log2(0.042),
                       },

              (1, 3): {'NP': log2(0.0049) + log2(0.14) + log2(0.1),
                       'VP': log2(0.6) + log2(0.0049) + log2(0.5),
                       'S': log2(0.14) + log2(0.007) + log2(0.9)},

              (2, 4): {'NP': log2(0.0049) + log2(0.14) + log2(0.1),
                       'VP': log2(0.1) + log2(0.00196) + log2(0.5),
                       'S': log2(0.35) + log2(0.042) + log2(0.9)},

              (1, 4): {'NP': log2(0.14) + log2(0.0000686) + log2(0.1),
                       'VP': log2(0.6) + log2(0.0000686) + log2(0.5),
                       'S': log2(0.0049) + log2(0.042) + log2(0.9)},
              }

        self.assertEqualPi(pi, parser._pi)

        bp = {(1, 1): {'N': Tree.fromstring("(N fish)"),
                       'V': Tree.fromstring("(V fish)"),
                       'NP': Tree.fromstring("(NP (N fish))"),
                       'VP': Tree.fromstring("(VP (V fish))"),
                       'S': Tree.fromstring("(S (VP (V fish)))")},

              (2, 2): {'N': Tree.fromstring("(N people)"),
                       'V': Tree.fromstring("(V people)"),
                       'NP': Tree.fromstring("(NP (N people))"),
                       'VP': Tree.fromstring("(VP (V people))"),
                       'S': Tree.fromstring("(S (VP (V people)))")},

              (3, 3): {'N': Tree.fromstring("(N fish)"),
                       'V': Tree.fromstring("(V fish)"),
                       'NP': Tree.fromstring("(NP (N fish))"),
                       'VP': Tree.fromstring("(VP (V fish))"),
                       'S': Tree.fromstring("(S (VP (V fish)))")},

              (4, 4): {'N': Tree.fromstring("(N tanks)"),
                       'V': Tree.fromstring("(V tanks)"),
                       'NP': Tree.fromstring("(NP (N tanks))"),
                       'VP': Tree.fromstring("(VP (V tanks))"),
                       'S': Tree.fromstring("(S (VP (V tanks)))")},

              (1, 2): {'NP': Tree.fromstring("""(NP (NP (N fish))
                                                    (NP (N people)))"""),
                       'VP': Tree.fromstring("""(VP (V fish)
                                                    (NP (N people)))"""),
                       'S': Tree.fromstring("""(S (VP (V fish)
                                                      (NP (N people))))""")},

              (2, 3): {'NP': Tree.fromstring("""(NP (NP (N people))
                                                    (NP (N fish)))"""),
                       'VP': Tree.fromstring("""(VP (V people)
                                                    (NP (N fish)))"""),
                       'S': Tree.fromstring("""(S (NP (N people))
                                                  (VP (V fish)))""")},

              (3, 4): {'NP': Tree.fromstring("""(NP (NP (N fish))
                                                    (NP (N tanks)))"""),
                       'VP': Tree.fromstring("""(VP (V fish)
                                                    (NP (N tanks)))"""),
                       'S': Tree.fromstring("""(S (VP (V fish)
                                                      (NP (N tanks))))""")},

              (1, 3): {'NP': Tree.fromstring("""(NP (NP (NP (N fish))
                                                        (NP (N people)))
                                                    (NP (N fish)))"""),
                       'VP': Tree.fromstring("""(VP (V fish)
                                                    (NP (NP (N people))
                                                        (NP (N fish))))"""),
                       'S': Tree.fromstring("""(S (NP (N fish))
                                                  (VP (V people)
                                                      (NP (N fish))))""")},

              (2, 4): {'NP': Tree.fromstring("""(NP (NP (NP (N people))
                                                        (NP (N fish)))
                                                    (NP (N tanks)))"""),
                       'VP': Tree.fromstring("""(VP (V people)
                                                    (NP (NP (N fish))
                                                        (NP (N tanks))))"""),
                       'S': Tree.fromstring("""(S (NP (N people))
                                                  (VP (V fish)
                                                      (NP (N tanks))))""")},

              (1, 4): {'NP': Tree.fromstring("""(NP (NP (N fish))
                                                    (NP (NP (NP (N people))
                                                            (NP (N fish)))
                                                        (NP (N tanks))))"""),
                       'VP': Tree.fromstring("""(VP (V fish)
                                                    (NP (NP (NP (N people))
                                                            (NP (N fish)))
                                                        (NP (N tanks))))"""),
                       'S': Tree.fromstring("""(S (NP (NP (N fish))
                                                      (NP (N people)))
                                                  (VP (V fish)
                                                      (NP (N tanks))))""")}}
        self.assertEqualPi(bp, parser._bp)

    def assertEqualPi(self, pi1, pi2):
        self.assertEqual(set(pi1.keys()), set(pi2.keys()))

        for k in pi1.keys():
            d1, d2 = pi1[k], pi2[k]
            self.assertEqual(d1.keys(), d2.keys(), k)
            for k2 in d1.keys():
                prob1 = d1[k2]
                prob2 = d2[k2]
                self.assertAlmostEqual(prob1, prob2)
