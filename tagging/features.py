from collections import namedtuple
from featureforge.feature import Feature, input_schema
from schema import Schema


# sent -- the whole sentence.
# prev_tags -- a tuple with the n previous tags.
# i -- the position to be tagged.
History = namedtuple('History', 'sent prev_tags i')


def check_rep_invariant(h):
    return type(h.sent) == list and\
           type(h.prev_tags) == tuple and\
           type(h.i) == int


def prev_tags(h):
    """Returns the prev_tags component of the given history

    h -- a history.
    """

    return h.prev_tags


@input_schema(History, check_rep_invariant)
def word_lower(h):
    """Feature: for the given history, it returns the current word in
    lower case.

    h -- a history.
    """
    sent, i = h.sent, h.i
    if i >= 0:
        ret = sent[i].lower()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


@input_schema(History, check_rep_invariant)
def word_istitle(h):
    """Feature: does the actual word begin in upper case?.

    h -- a history.
    """
    sent, i = h.sent, h.i
    if i >= 0:
        ret = sent[i].istitle()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


@input_schema(History, check_rep_invariant)
def word_isupper(h):
    """Feature: is the actual word in upper case?.

    h -- a history.
    """
    sent, i = h.sent, h.i

    if i >= 0:
        ret = sent[i].isupper()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


@input_schema(History, check_rep_invariant)
def word_isdigit(h):
    """Feature: is the actual word a digit?.

    h -- a history.
    """
    sent, i = h.sent, h.i

    if i >= 0:
        ret = sent[i].isdigit()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


class NPrevTags(Feature):
    input_schema = Schema(History, check_rep_invariant)
    output_schema = Schema(tuple, lambda t: len(t) == self._n)

    def __init__(self, n):
        """Feature: n previous tags tuple.

        n -- number of previous tags to consider.
        """
        self._n = n

    def _evaluate(self, h):
        """n previous tags tuple.

        h -- a history.
        """
        prev_tags = h.prev_tags
        return prev_tags[len(prev_tags) - self._n:]


class PrevWord(Feature):
    input_schema = Schema(History, check_rep_invariant)

    def __init__(self, f):
        """Feature: the feature f applied to the previous word.

        f -- the feature.
        """
        self._f = f

    def _evaluate(self, h):
        """Apply the feature to the previous word in the history.

        h -- the history.
        """

        new_h = History(list(h.sent), tuple(h.prev_tags), h.i - 1)

        return str(self._f(new_h))
