from math import log2
from collections import defaultdict


class HMM:
    beginning_symbol = ['<s>']
    stop_symbol = ['</s>']

    def __init__(self, n, tagset, trans, out):
        """
        n -- n-gram size.
        tagset -- set of tags.
        trans -- transition probabilities dictionary.
        out -- output probabilities dictionary.
        """
        self._n = n
        self._tagset = tagset
        self._trans = trans
        self._out = out

    def tagset(self):
        """Returns the set of tags.
        """
        return self._tagset

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        ret = 0.0

        if self._n == 1:
            prev_tags = ()

        if prev_tags in self._trans and tag in self._trans[prev_tags]:
            ret = self._trans[prev_tags][tag]

        return ret

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """

        ret = 0.0

        if tag in self._out and word in self._out[tag]:
            ret = self._out[tag][word]

        return ret

    def tag_prob(self, y):
        """Probability of a tagging.
        Warning: subject to underflow problems.

        y -- tagging.
        """
        context = tuple((self._n - 1) * HMM.beginning_symbol)
        y_extended = tuple(y + HMM.stop_symbol)
        prob = 1.0

        # INV : {context has the probability context for the actual tag}
        for tag in y_extended:
            prob *= self.trans_prob(tag, context)
            if self._n > 1:
                context = context[1:] + (tag,)

        return prob

    def prob(self, x, y):
        """Joint probability of a sentence and its tagging.
        Warning: subject to underflow problems.

        x -- sentence.
        y -- tagging.
        """
        o_prob = 1.0
        tagging_prob = self.tag_prob(y)

        for i in range(len(x)):
            o_prob *= self.out_prob(x[i], y[i])

        return tagging_prob*o_prob

    def tag_log_prob(self, y):
        """Log-probability of a tagging.

        y -- tagging.
        """
        context = tuple((self._n - 1) * HMM.beginning_symbol)
        y_extended = tuple(y + HMM.stop_symbol)
        prob = 0.0

        # INV : {context has the probability context for the actual tag}
        for tag in y_extended:
            prob += log2(self.trans_prob(tag, context))
            if self._n > 1:
                context = context[1:] + (tag,)

        return prob

    def log_prob(self, x, y):
        """Joint log-probability of a sentence and its tagging.

        x -- sentence.
        y -- tagging.
        """
        o_prob = 0.0
        tagging_prob = self.tag_log_prob(y)

        i = 0
        for i in range(len(x)):
            o_prob += log2(self.out_prob(x[i], y[i]))

        return tagging_prob + o_prob

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        tagger = ViterbiTagger(self)
        return tagger.tag(self)


class ViterbiTagger:

    def __init__(self, hmm):
        """
        hmm -- the HMM.
        """
        self._hmm = hmm
        self._pi = {}

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        # Initialization.
        n = self._hmm._n
        self._pi = {0: {tuple((n-1) * HMM.beginning_symbol): (log2(1.0), [])}}
        m = len(sent)

        for k in range(1, m+1):
            self._pi[k] = pi_k = {}
            # Search for any tag with out_prob > 0.
            for v in self._hmm.tagset():
                o_prob = self._hmm.out_prob(sent[k-1], v)
                if o_prob > 0.0:
                    # Search for previous tags with trans_prob > 0.
                    for prev_tags in self._pi[k-1]:
                        t_prob = self._hmm.trans_prob(v, prev_tags)

                        if t_prob > 0.0:
                            prev_prob, prev_tagging = self._pi[k-1][prev_tags]

                            prob = prev_prob + log2(t_prob) + log2(o_prob)

                            tags = prev_tags[1:] + (v,)

                            if tags not in pi_k or prob > pi_k[tags][0]:
                                # New item or new max. prob. found.
                                pi_k[tags] = (prob, prev_tagging + [v])

        # Extract the best tagging.
        max_prob = float('-inf')
        max_tag = None
        pi_m = self._pi[m]
        for context in pi_m:
            t_prob = self._hmm.trans_prob(HMM.stop_symbol[0], context)

            if t_prob > 0.0:
                prev_prob, prev_tagging = pi_m[context]
                prob = prev_prob + log2(t_prob)

                if max_prob < prob:
                    max_prob = prob
                    max_tag = prev_tagging

        return max_tag


class MLHMM(HMM):

    def __init__(self, n, tagged_sents, addone=True):
        """n -- order of the model.
        tagged_sents -- training sentences, each one being a list of pairs.
        addone -- whether to use addone smoothing (default: True).
        """
        self._n = n
        # we use float as the default factory, to count in floats, to
        # avoid having to cast to float each time we compute a prob.
        # using this counts
        self._tags_counts = defaultdict(float)
        self._tagged_words_counts = defaultdict(float)
        self._tagset = set()
        self._words = set()
        self._len_words = 0.0
        self._addone = addone
        self._tagger = ViterbiTagger(self)

        for sent in tagged_sents:
            tags = []
            # Count of words and tags.
            for tagged_word in sent:
                self._tagged_words_counts[tagged_word] += 1.0
                word = tagged_word[0]
                self._words.add(word)
                tag = tagged_word[1]
                self._tagset.add(tag)
                tags.append(tag)
                if n > 2:
                    # We also need the counting of the occurrences of each
                    # tag. If n > 2 => in the next loop, when counting n and
                    # n-1 grams, the counting of each tag will not be done.
                    self._tags_counts[(tag,)] += 1

            tags_extended = (n-1)*HMM.beginning_symbol + tags + HMM.stop_symbol

            for i in range(len(tags_extended) - n + 1):
                ngram = tuple(tags_extended[i: i + n])
                self._tags_counts[ngram] += 1.0
                self._tags_counts[ngram[:-1]] += 1.0

        self._len_words = len(self._words)
        self._len_tagset = len(self._tagset)

        # Convert defaultdicts to dicts, to avoid errors (when indexing
        # with an non-existing key).
        self._tags_counts = dict(self._tags_counts)
        self._tagged_words_counts = dict(self._tagged_words_counts)

    def tcount(self, tokens):
        """Count for an k-gram for k <= n.

        tokens -- the k-gram tuple.
        """
        ret = 0
        if tokens in self._tags_counts:
            ret = self._tags_counts[tokens]

        return ret

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return w not in self._words

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        ret = 0.0

        if self._n == 1:
            prev_tags = ()

        if self._addone:
            ret = (self.tcount(prev_tags + (tag,)) + 1.0) / \
                (self.tcount(prev_tags) + self._len_tagset)
        else:
            # {not self._addone}
            if prev_tags in self._tags_counts:
                ret = self.tcount(prev_tags + (tag,)) / self.tcount(prev_tags)

        return ret

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        ret = 0.0
        tcount = self.tcount((tag,))

        if self.unknown(word) or tcount == 0:
            ret = 1.0/self._len_words
        else:
            # {not self.unknown(word) and self.tcount((tag,)) != 0}
            if (word, tag) in self._tagged_words_counts:
                ret = self._tagged_words_counts[(word, tag)] / tcount
            else:
                ret = 0.0

        return ret

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        return self._tagger.tag(sent)
