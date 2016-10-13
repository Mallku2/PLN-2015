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

    return h.prev_tags


def word_lower(h):
    """For the given history, it returns the actual word (indicated in h)
    lowercased.

    h -- a history.
    """
    sent, i = h.sent, h.i
    if i >= 0:
        ret = sent[i].lower()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


def word_istitle(h):
    """Feature: the actual word begins in upper case.

    h -- a history.
    """
    sent, i = h.sent, h.i
    if i >= 0:
        ret = sent[i][0].isupper() and sent[i][1:].islower()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


def word_isupper(h):
    """Feature: the actual word is in upper case.

    h -- a history.
    """
    sent, i = h.sent, h.i

    if i >= 0:
        ret = sent[i].isupper()
    else:
        # {i < 0}
        ret = 'BOS'

    return ret


def word_isdigit(h):
    """Feature: the atual word is a digit.

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
