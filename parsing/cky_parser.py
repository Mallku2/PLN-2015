from math import log2
from nltk.tree import Tree


class CKYParser:

    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        self._grammar = grammar
        self._start_s = self._grammar.start().symbol()
        self._pi = {}
        self._bp = {}

        # Cache for the productions of the grammar.
        self._prods = {}

        productions = self._grammar.productions()

        for prod in productions:
            rhs = prod.rhs()    
            if len(rhs) == 2:
                key = (rhs[0].symbol(), rhs[1].symbol())
            else:
                # {len(rhs) != 2}
                # It is a production of the form X->e, with e, a terminal
                # symbol.
                key = (rhs[0],)

            if key not in self._prods:
                self._prods[key] = {}

            self._prods[key][prod.lhs().symbol()] = log2(prod.prob())

    def parse(self, sent):
        """Parse a sequence of terminals.

        sent -- the sequence of terminals.
        """

        n = len(sent)
        # Initialize the dynamic table.
        self._pi = {}
        self._bp = {}

        for i in range(n):
            word = sent[i]
            key = (word,)
            if key not in self._prods:
                return float("-inf"), None

            productions = self._prods[key]
            pos = i + 1
            index = (pos, pos)
            self._pi[index] = pi_value = {}
            self._bp[index] = bp_value = {}

            for nt, prob in productions.items():
                pi_value[nt] = prob
                bp_value[nt] = Tree(nt, [word])

        # Length of an interval of words, into sent.
        for i_l in range(1, n):
            # Position (into sent) of the beginning of the interval.
            for i in range(1, n - i_l + 1):
                j = i + i_l
                index = (i, j)

                self._pi[index] = actual_pi_int = {}
                self._bp[index] = actual_bp_int = {}

                # Point of splitting.
                for s in range(i, j):
                    left_int_index = (i, s)
                    right_int_index = (s + 1, j)

                    pi_left_dict = self._pi[left_int_index]
                    pi_right_dict = self._pi[right_int_index]
                    bp_left_dict = self._bp[left_int_index]
                    bp_right_dict = self._bp[right_int_index]

                    for no_t_y in pi_left_dict:
                        for no_t_z in pi_right_dict:
                            key = (no_t_y, no_t_z)
                            prob_y = pi_left_dict[no_t_y]
                            prob_z = pi_right_dict[no_t_z]
                            tree_y = bp_left_dict[no_t_y]
                            tree_z = bp_right_dict[no_t_z]

                            if key in self._prods:
                                ps = self._prods[key]
                            else:
                                # {key not in self._prods}
                                ps = {}

                            for nt, p in ps.items():
                                prob = p + prob_y + prob_z
                                if nt not in self._pi[index]:
                                    actual_pi_int[nt] = float("-inf")
                                    actual_bp_int[nt] = None

                                # {nt in self._pi[index]}
                                if prob > self._pi[index][nt]:
                                    actual_pi_int[nt] = prob
                                    actual_bp_int[nt] = Tree(nt,
                                                             [tree_y,
                                                              tree_z])

        # Determine if the parsing was successful.
        last_index = (1, n)
        if last_index in self._pi and self._start_s in self._pi[last_index]:
            ret = (self._pi[last_index][self._start_s],
                   self._bp[last_index][self._start_s])
        else:
            # {(1, n) not in self._pi or self._start_s not in self._pi[(1, n)]}
            ret = (float("-inf"), None)

        return ret
