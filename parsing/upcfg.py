from nltk.tree import Tree
from nltk.grammar import Nonterminal, induce_pcfg
from parsing.cky_parser import CKYParser
from parsing.util import lexicalize, unlexicalize


class UPCFG:
    """Unlexicalized PCFG.
    """

    def __init__(self, parsed_sents, start='sentence', horzMarkov=None,
                 unary=True):
        """
        parsed_sents -- list of training trees.
        """
        self._pcfg = None
        self._parser = None
        self._start = start

        # Productions in CNF.
        productions = []

        for parsed_sent in parsed_sents:
            t_copy = parsed_sent.copy(deep=True)
            unlexicalize(t_copy)

            t_copy.chomsky_normal_form(horzMarkov=horzMarkov)

            if not unary:
                t_copy.collapse_unary(collapsePOS=True)

            productions += t_copy.productions()

        self._pcfg = induce_pcfg(Nonterminal(start), productions)
        self._parser = CKYParser(self._pcfg, unary)

    def productions(self):
        """Returns the list of UPCFG probabilistic productions.
        """
        return self._pcfg.productions()

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """

        tags = [tag_word[1] for tag_word in tagged_sent]
        words = [tag_word[0] for tag_word in tagged_sent]
        prob, parse_tree = self._parser.parse(tags)

        if parse_tree is not None:
            parse_tree = parse_tree.copy(deep=True)
            parse_tree.un_chomsky_normal_form()
            lexicalize(parse_tree, words)

            ret = parse_tree
        else:
            subtree = [Tree(tag_word[1], [tag_word[0]])
                       for tag_word in tagged_sent]

            ret = Tree(self._start, subtree)

        return ret
