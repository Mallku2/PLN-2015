from math import log2
from nltk.tree import Tree
from itertools import product

class CKYParser:

    def __init__(self, grammar, unary):
        """
        grammar -- a binarised NLTK PCFG.
        """
        self._grammar = grammar
        self._start_s = self._grammar.start().symbol()
        self._pi = {}
        self._bp = {}
        self._unary = unary

        # Cache for the productions of the grammar: dictionary of the form
        # { 'binaries' : {rhs-non-terminals x {lhs-non-terminal x log_prob} }
        #   'unaries'  : {rhs-non-terminal x {lhs-non-terminal x log_prob} }
        #   'lexicon' :  {rhs-terminal x {lhs-non-terminal x log_prob} }}
        self._prods = {'binaries': {},
                       'unaries': {},
                       'lexicon': {}}

        productions = self._grammar.productions()
        type_prods = None
        for prod in productions:
            rhs = prod.rhs()
            add = True

            if len(rhs) == 2:
                key = (rhs[0].symbol(), rhs[1].symbol())
                type_prods = 'binaries'
            else:
                # {len(rhs) != 2}
                assert(len(rhs) == 1)

                if prod.is_lexical():
                    # It is a production of the form X->e, with e, a terminal
                    # symbol.
                    type_prods = 'lexicon'
                    key = rhs[0]
                else:
                    # {not prod.is_lexical()}

                    # When the original parsing-tree, from which we obtaing the
                    # PCFG, contains an unary production of the form
                    # self._start_s -> A, with A a non-terminal symbol, even
                    # collapse_unary doesn't get rid of such productions.
                    if not self._unary:
                        add = False
                    else:
                        type_prods = 'unaries'
                        key = rhs[0].symbol()

            if add:
                if key not in self._prods[type_prods]:
                    self._prods[type_prods][key] = {}

                self._prods[type_prods][key][prod.lhs().symbol()] = log2(
                                                                    prod.prob())


    def _init_dynamic_tables(self, sent):
        ret = True  # Was initilization done?
        # Initialize the dynamic table.
        self._pi = {}
        self._bp = {}

        for i in range(len(sent)):
            word = sent[i]

            if word not in self._prods['lexicon']:
                ret = False
                break

            # {key in self._prods['unaries']}

            productions = self._prods['lexicon'][word]
            pos = i + 1
            index = (pos, pos)
            self._pi[index] = pi_value = {}
            self._bp[index] = bp_value = {}

            for nt, prob in productions.items():
                pi_value[nt] = prob
                bp_value[nt] = Tree(nt, [word])

            # Handle unaries: taken from
            # https://www.youtube.com/watch?v=hq80J8kBg-Y&t=1043s
            if self._unary:
                self._handle_unaries(pi_value, bp_value)

        return ret

    def _handle_unaries(self, pi_value, bp_value):
        # Handle unaries: taken from
        # https://www.youtube.com/watch?v=hq80J8kBg-Y&t=1043s

        # Each time we repeat the loop, we "go up" one level into the parsing
        # tree, using an unary production, towards the starting non-terminal,
        added = True
        un_prods = self._prods['unaries']
        while added:
            added = False
            keys = set(pi_value.keys()) & set(un_prods.keys())

            for rhs_nt in keys:
                for lhs_nt, prob in un_prods[rhs_nt].items():
                    new_prob = prob + pi_value[rhs_nt]

                    if (lhs_nt in pi_value and new_prob > pi_value[lhs_nt])\
                            or lhs_nt not in pi_value:

                        pi_value[lhs_nt] = new_prob
                        bp_value[lhs_nt] = Tree(lhs_nt,
                                                [Tree(rhs_nt,
                                                      bp_value[rhs_nt])])
                        added = True

    def _handle_binaries(self, left_int_index, right_int_index, actual_pi_int,
                         actual_bp_int):

        pi_left_dict = self._pi[left_int_index]
        pi_right_dict = self._pi[right_int_index]
        bin_prods = self._prods['binaries']

        for key in product(pi_left_dict, pi_right_dict):
            if key in bin_prods:
                (no_t_y, no_t_z) = key
                prob_y = pi_left_dict[no_t_y]
                prob_z = pi_right_dict[no_t_z]

                for nt_root, p in bin_prods[key].items():
                    prob = p + prob_y + prob_z

                    if nt_root not in actual_pi_int or \
                            prob > actual_pi_int[nt_root]:

                        actual_pi_int[nt_root] = prob
                        tree_y = self._bp[left_int_index][no_t_y]
                        tree_z = self._bp[right_int_index][no_t_z]
                        actual_bp_int[nt_root] = Tree(nt_root,
                                                      [tree_y,
                                                       tree_z])

    def parse(self, sent):
        """Parse a sequence of terminals.

        sent -- the sequence of terminals.
        """
        ret = None
        n = len(sent)

        init_done = self._init_dynamic_tables(sent)

        if not init_done:
            return (float("-inf"), None)

        # Length of an interval of words, into sent.
        for span in range(1, n):
            # Position (into sent) of the beginning of the interval.
            for begin in range(1, n - span + 1):
                end = begin + span
                index = (begin, end)

                self._pi[index] = actual_pi_int = {}
                self._bp[index] = actual_bp_int = {}

                # Point of splitting.
                for s in range(begin, end):
                    left_int_index = (begin, s)
                    right_int_index = (s + 1, end)

                    self._handle_binaries(left_int_index, right_int_index,
                                          actual_pi_int, actual_bp_int)

                if self._unary:
                    self._handle_unaries(actual_pi_int, actual_bp_int)

        # Determine if the parsing was successful.
        last_index = (1, n)
        if last_index in self._pi and self._start_s in self._pi[last_index]:
            ret = (self._pi[last_index][self._start_s],
                   self._bp[last_index][self._start_s])
        else:
            # {(1, n) not in self._pi or self._start_s not in self._pi[(1, n)]}
            ret = (float("-inf"), None)

        return ret
