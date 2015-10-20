from collections import namedtuple

from featureforge.feature import Feature


# sent -- the whole sentence.
# prev_tags -- a tuple with the n previous tags.
# i -- the position to be tagged.
History = namedtuple('History', 'sent prev_tags i')

def prev_tags(h):
    """Returns the prev_tags component of the given history
    
    h -- a history.
    """
    return h[1]

def word_lower(h):
    """Feature: current lowercased word.

    h -- a history.
    """
    sent, i = h.sent, h.i
    return sent[i].lower()

def word_istitle(h):
    """Feature: current lowercased word.

    h -- a history.
    """
    # TODO: sólo chequeamos la primer letra?
    sent, i = h.sent, h.i
    return sent[i][0].isupper() and sent[i][1:].islower()

def word_isupper(h):
    """Feature: current lowercased word.

    h -- a history.
    """
    sent, i = h.sent, h.i
    
    return sent[i].isupper()

def word_isdigit(h):
    """Feature: current lowercased word.

    h -- a history.
    """
    sent, i = h.sent, h.i
    
    return sent[i].isdigit()


class NPrevTags(Feature):

    def __init__(self, n):
        """Feature: n previous tags tuple.

        n -- number of previous tags to consider.
        """
        self.n = n

    def _evaluate(self, h):
        """n previous tags tuple.

        h -- a history.
        """
        return h[1][len(h[1]) - self.n:]


class PrevWord(Feature):
    # TODO: bag-of-words?
    def __init__(self, f):
        """Feature: the feature f applied to the previous word.
 
        f -- the feature.
        """
        self.f = f

    def _evaluate(self, h):
        """Apply the feature to the previous word in the history.

        h -- the history.
        """
        # TODO: este history esta bien?.
        # TODO: me falta tratar los casos en los que h[2]-1 < 0 => se devuelve
        # BOS
        new_h = History(h[0],h[1],h[2]-1)
        return self.f(new_h)