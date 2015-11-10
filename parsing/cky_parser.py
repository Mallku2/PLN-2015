from math import log2
from nltk.grammar import Nonterminal
from nltk.tree import Tree

class CKYParser:
 
    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        # TODO: aparentemente podemos asumir que recibimos siempre sólo
        # Chomsky Normal Form.
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
                key = str(rhs[0]) + ' ' + str(rhs[1])
            else:
                # {len(rhs) != 2}
                # It is a production of the form X->e, with e, a terminal 
                # symbol.
                key = str(rhs[0])
                
            if key not in self._prods:
                self._prods[key] = {}
                
            lhs = prod.lhs().symbol()
            
            self._prods[key][lhs] = log2(prod.prob())
 
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
            # TODO: la semántica de productions, indica que me están 
            # devolviendo las producciones cuyo lado derecho comienza con 
            # word...
            
            if not word in self._prods:
                # TODO: arreglar este caso. Notar que los errores que obtengo
                # al ejecutar eval pueden deberse a que estoy intentando
                # hacer parsing sobre la oración de tags, que construyo a
                # partir de la oración etiquetada que recibo. Pero mi cky_parser
                # tiene internamente conocimiento de las producciones que
                # resultaron de agarrar los árboles de parseo originales, y
                # ejecutar sobre ellos las transformaciones que los llevan a
                # FNC y elimina producciones unarias. Este proceso puede alterar
                # los no-terminales originales, y quizás de allí que 
                # cuando entramos acá e intentamos indexar con una etiqueta,
                # esta resulta desconocida.
                print("mal1")
                return float("-inf"), None
                
            productions = self._prods[word]
            pos = i + 1
            index = (pos, pos)
            self._pi[index] = {}
            self._bp[index] = {}
            
            for nt in productions:
                # TODO: asumo que prob() != 0
                self._pi[index][nt] = productions[nt]
                                                        
                self._bp[index][nt] = Tree.fromstring('(' + 
                                                      nt + 
                                                      ' ' + 
                                                      word +
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

                    # TODO: esto se podría hacer con un único bucle que itere
                    # variables no_t_y y no_t_z dentro de zip(self._pi etc etc)
                    for no_t_y in self._pi[left_int_index]:
                        for no_t_z in self._pi[right_int_index]:
                            key = no_t_y + ' ' + no_t_z

                            if key in self._prods:
                                ps = self._prods[key]
                            else:
                                # {key not in self._prods}
                                ps = {}

                            # TODO: fijarse que podríamos directamente extraer
                            # las probabilidades de ps desde la definición del
                            # bucle...
                            for nt in ps:
                                # TODO: asumo que prob != 0?
                                prob = ps[nt] + \
                                self._pi[left_int_index][no_t_y] + \
                                self._pi[right_int_index][no_t_z]


                                if nt not in self._pi[index]:
                                    self._pi[index] = {}
                                    self._bp[index] = {}

                                self._pi[index][nt] = prob

                                tree = Tree(nt, 
                                        [self._bp[left_int_index][no_t_y],
                                        self._bp[right_int_index][no_t_z]])

                                self._bp[index][nt] = tree
        
        if (1, n) in self._pi and self._start_s in self._pi[(1, n)]:
            # The parsing was successful.
            ret = (self._pi[(1, n)][self._start_s], 
                   self._bp[(1, n)][self._start_s])
            print("bien")
        else:
            # {(1, n) not in self._pi or self._start_s not in self._pi[(1, n)]}
            ret = (float("-inf"), None)
            print("mal2")
            
        return ret
