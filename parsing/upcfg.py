from nltk.tree import Tree
from nltk.grammar import Production, ProbabilisticProduction, PCFG, Nonterminal
from parsing.cky_parser import CKYParser


class UPCFG:
    """Unlexicalized PCFG.
    """
 
    def __init__(self, parsed_sents, start='sentence'):
        """
        parsed_sents -- list of training trees.
        """
        self._productions = []
        self._parser = None
        self._start = start
        
        org_prods = []
        for parsed_sent in parsed_sents:
            # TODO: hacer un test que me muestre que efecitivamente stamos
            # convirtiendo adecuadamente la gramatica a Chonsky Normal Form
            
            
            parsed_sent.chomsky_normal_form()
            parsed_sent.collapse_unary(collapsePOS = True,
                                       collapseRoot = True)
            aux = parsed_sent.productions()
            org_prods += aux
            """for prod in aux:
                if (prod.is_lexical() and len(prod.rhs()) != 1) or\
                       (prod.is_nonlexical() and len(prod.rhs()) != 2):
                    
                    print("prod: "+str(prod))
                    print("is_lexical: "+str(prod.is_lexical()))
                    print("is_nonlexical: "+str(prod.is_nonlexical()))
                    print("len(prod.rhs()): "+str(len(prod.rhs())))
                    parsed_sent.draw()
                    assert(False)"""

        # Contabilice each production and delete lexical information.
        dict_aux = {}
        for prod in org_prods:
            # Have we found lexical information?
            found_lexical = False

            lhs = prod.lhs()
            
            if lhs not in dict_aux:
                # list(Total occurrences of productions of lhs, 
                #      dict(rhs x occurrences of lhs->rhs))
                dict_aux[lhs] = [0, {}]

            dict_aux[lhs][0] += 1
            
            # {lhs in dict_aux}
            rhs = prod.rhs()
            prod_is_lexical = prod.is_lexical()
            
            if prod_is_lexical:
                if (lhs.symbol(),) not in dict_aux[lhs][1]:
                    dict_aux[lhs][1][(lhs.symbol(),)] = 1
                else:
                    dict_aux[lhs][1][(lhs.symbol(),)] += 1
            else:
                if rhs not in dict_aux[lhs][1]:
                    dict_aux[lhs][1][rhs] = 1
                else:
                    dict_aux[lhs][1][rhs] += 1

        # Calculate probabilities.
        for lhs in dict_aux:
            total = dict_aux[lhs][0]
            rhs_counts = dict_aux[lhs][1]
            sum = 0.0

            for rhs, count in rhs_counts.items():
                prob = count / total
                sum += prob
                self._productions.append(ProbabilisticProduction(lhs, 
                                                                 rhs,
                                                                 prob = prob))

        self._parser = CKYParser(PCFG(Nonterminal(start), self._productions))

    def productions(self):
        """Returns the list of UPCFG probabilistic productions.
        """
        return self._productions
 
    def parse(self, tagged_sent):
        """Parse a tagged sentence.
 
        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """

        """
        aunque me debe faltar algo porque no anda muy bien, pero alomejor te 
        puedo ayudar
        
        Ezequiel
        No termino de entender q hay q hacer, me imagino q llamas a cky para q 
        te de el arbol "deslexicalizado" Y despues q haces?
        
        Pablo
        la tagged sent que recibis de entrada, la separas en palabras y tags
        y llamas a cky como vos dijiste, pero pasandole los tags
        te fijas, si el arbol que devolvio cky es None, quiere decir que no 
        encontro un parseo, entonces tenes que devolver un arbol chato
        si el arbol no es None, entonces lo lexicalizas con los tokens y 
        devolves eso
        
        Ezequiel
        Ahah buenisimo
        No sabia cuando devolver el flat
        Voy a probar, gracias Pablo!
        """
        tags = [tag_word[1] for tag_word in tagged_sent]
        words = [tag_word[0] for tag_word in tagged_sent]

        prob, parse_tree = self._parser.parse(tags)

        if parse_tree != None:
            i = 0

            for pos in parse_tree.treepositions('leaves'):
                parse_tree[pos] = words[i]
                i += 1

            ret = parse_tree
        else:
            subtree = [Tree(tag_word[1], [tag_word[0]]) 
                       for tag_word in tagged_sent]

            ret = Tree(self._start, subtree)

        return ret