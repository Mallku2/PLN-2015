from nltk.tree import Tree


class Flat:
    '''2 levels parse-tree: root node, POS tags and words.
    '''
    def __init__(self, parsed_sents, start='sentence'):
        self.start = start

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        t = Tree(self.start, [Tree(tag, [word]) for word, tag in tagged_sent])
        return t


class RBranch:
    '''Same as Flat, but converts the resulting into its CNF equivalent,
    with right factoring.
    '''
    def __init__(self, parsed_sents, start='sentence'):
        self.start = start

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        t = Tree(self.start, [Tree(tag, [word]) for word, tag in tagged_sent])
        t.chomsky_normal_form(factor='right', horzMarkov=0)
        return t


class LBranch:
    '''Same as Flat, but converts the resulting into its CNF equivalent,
    with left factoring.
    '''
    def __init__(self, parsed_sents, start='sentence'):
        self.start = start

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        t = Tree(self.start, [Tree(tag, [word]) for word, tag in tagged_sent])
        t.chomsky_normal_form(factor='left', horzMarkov=0)
        return t
