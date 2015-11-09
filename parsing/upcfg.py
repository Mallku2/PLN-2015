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
            org_prods += parsed_sent.productions()
        
        # Contabilice each production and delete lexical information.
        dict_aux = {}
        for prod in org_prods:
            lhs = prod.lhs()
            
            if lhs not in dict_aux:
                dict_aux[lhs] = {}
            
            # TODO: cambiar el comnetario cuando cambie el ombre del diccionario    
            # {lhs in aux}
            rhs = prod.rhs()
            prod_is_lexical = prod.is_lexical()
            
            if rhs not in dict_aux[lhs]:
                # Delete lexical information.
                if prod_is_lexical:
                    # Then, as it is in Chosmky Normal Form, it must be a
                    # production of the form Nonterminal -> Terminal.
                    # We'll count the production just once.
                    dict_aux[lhs][(lhs.symbol(),)] = 1
                else:
                    # {not prod_is_lexical}
                    dict_aux[lhs][rhs] = 0

            if not prod_is_lexical:
                # {rhs in dict_aux[lhs]}
                dict_aux[lhs][rhs] += 1

        # Calculate probabilities.
        for lhs in dict_aux:
            total = float(len(dict_aux[lhs]))

            for rhs, count in dict_aux[lhs].items():
                prob = count / total
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