from math import log2
from nltk.grammar import Nonterminal
from nltk.tree import Tree

class CKYParser:
 
    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        self._grammar = grammar
        self._pi = {}
        self._bp = {}
 
    def parse(self, sent):
        """Parse a sequence of terminals.
 
        sent -- the sequence of terminals.
        """

        n = len(sent)

        # Initialize the dynamic table.
        # TODO: _pi tiene la forma: 
        # {pos. de comienzo en la oracion x pos. de fin en la oracion x 
        #    {head del constituyente de max. prob x max prob}}
        self._pi = {}
        for i in range(n):
            word = sent[i]
            # TODO: asumimos que las producciones, si tienen 2 símbolos en
            # su lado derecho => son no-terminales?
            # TODO: la semántica de productions, indica que me están devolviendo
            # las producciones cuyo lado derecho comienza con word...
            productions = [prod for prod in 
                                        self._grammar.productions(rhs = word)
                            if len(prod.rhs()) == 1]
            pos = i + 1
            index = (pos, pos)
            self._pi[index] = {}
            self._bp[index] = {}
            
            for prod in productions:
                nt = prod.lhs().symbol()
                
                # TODO: asumo que prob() != 0
                self._pi[index][nt] = log2(prod.prob())
                
                lhs = prod.lhs().symbol()
                rhs = prod.rhs()[0]
                                                        
                self._bp[index][nt] = Tree.fromstring('(' + 
                                                      lhs + 
                                                      ' ' + 
                                                      rhs +
                                                      ')')
        # Length of an interval of words, into sent.
        for i_l in range(1, n + 1):
            # Position (into sent) of the beginning of the interval.
            for i in range(n - i_l + 1):
                index = (i + 1, i + i_l)
                
                if not index in self._pi:
                    self._pi[index] = {}
                    self._bp[index] = {}
                
                # Splitting: length of the left segment.
                for s_l in range(1, i_l):
                    left_int_index = (i + 1, i + s_l)
                    right_int_index = (i + s_l + 1, i + i_l)
                    
                    for no_t_y in self._pi[left_int_index]:
                        for no_t_z in self._pi[right_int_index]:
                            rhs = (Nonterminal(no_t_y), Nonterminal(no_t_z))

                            ps = [prod 
                                  for prod in 
                                  self._grammar.productions(rhs = \
                                                        Nonterminal(no_t_y))
                                  if prod.rhs() == rhs]
                            
                            for prod in ps:
                                lhs = prod.lhs().symbol()
                                # TODO: asumo que prob != 0?
                                prob = log2(prod.prob()) + \
                                self._pi[left_int_index][no_t_y] + \
                                self._pi[right_int_index][no_t_z]

                                if lhs not in self._pi[index]:
                                    self._pi[index] = {}
                                    self._bp[index] = {}
                                
                                self._pi[index][lhs] = prob

                                tree = Tree(lhs, 
                                        [self._bp[left_int_index][no_t_y],
                                        self._bp[right_int_index][no_t_z]])

                                self._bp[index][lhs] = tree

        return self._pi[(1, n)]['S'], self._bp[(1, n)]['S']
                            