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

        i = 0
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
        # TODO: por qué tagger no es un atributo de la instancia???...
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
        self._pi = {}
        self._pi[0] = {}
        self._pi[0][tuple((self._hmm._n-1)*HMM.beginning_symbol)] = (log2(1.0),
                                                                     [])

        m = len(sent)
        for k in range(1, m+1):
            self._pi[k] = {}
            # Search for any tag with out_prob > 0.
            for v in self._hmm.tagset():
                o_prob = self._hmm.out_prob(sent[k-1], v)
                if o_prob > 0.0:
                    # Search for previous tags with trans_prob > 0.
                    for prev_tags in self._pi[k-1]:
                        if self._hmm._n > 1:
                            t_prob = self._hmm.trans_prob(v, prev_tags)
                        else:
                            t_prob = self._hmm.trans_prob(v, ())
                        if t_prob > 0.0:
                            prob = self._pi[k-1][prev_tags][0] + \
                                log2(t_prob) + log2(o_prob)

                            tags = prev_tags[1:] + (v,)

                            if tags not in self._pi[k] or prob > self._pi[k][tags][0]:
                                # New item or new max. prob. found.
                                self._pi[k][tags] = (prob,
                                                     self._pi[k-1]
                                                     [prev_tags][1] + [v])

        # Extract the best tagging.
        max_prob = float('-inf')
        max_tag = None

        for context in self._pi[m]:
            if self._hmm._n > 1:
                t_prob = self._hmm.trans_prob(HMM.stop_symbol[0], context)
            else:
                t_prob = self._hmm.trans_prob(HMM.stop_symbol[0], ())
            if t_prob > 0.0:
                prob = self._pi[m][context][0] + log2(t_prob)

                if max_prob < prob:
                    max_prob = prob
                    max_tag = self._pi[m][context][1]

        return max_tag


class MLHMM(HMM):

    def __init__(self, n, tagged_sents, addone=True):
        """n -- order of the model.
        tagged_sents -- training sentences, each one being a list of pairs.
        addone -- whether to use addone smoothing (default: True).
        """
        self._n = n
        self._tags_counts = defaultdict(int)
        self._tagged_words_counts = defaultdict(int)
        self._tagset = set()
        self._words = set()
        self._len_words = 0.0
        self._addone = addone
        self._tagger = ViterbiTagger(self)

        for sent in tagged_sents:
            tags = []
            # Count of words and tags.
            for tagged_word in sent:
                self._tagged_words_counts[tagged_word] += 1
                self._words.add(tagged_word[0])
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
                self._tags_counts[ngram] += 1
                self._tags_counts[ngram[:-1]] += 1

        self._len_words = len(self._words)

        # Convert defaultdicts to dicts, to avoid errors.
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

        if self._addone:
            ret = (self.tcount(prev_tags + (tag,)) + 1.0) / \
                (self.tcount(prev_tags) + self._len_words)
        else:
            # {not self._addone}
            if prev_tags in self._tags_counts:
                ret = self.tcount(prev_tags + (tag,)) / \
                    float(self.tcount(prev_tags))

        return ret

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        ret = 0.0
        if self.unknown(word) or self.tcount((tag,)) == 0:
            ret = 1.0/self._len_words
        else:
            # {not self.unknown(word) and self.tcount((tag,)) != 0}
            if (word, tag) in self._tagged_words_counts:
                ret = self._tagged_words_counts[(word, tag)] / \
                    float(self.tcount((tag,)))
            else:
                ret = 0.0

        return ret

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        return self._tagger.tag(sent)
