from featureforge.vectorizer import Vectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from tagging.features import History, word_lower, word_istitle, word_isupper,\
    word_isdigit, NPrevTags, PrevWord


class MEMM:
    def __init__(self, n, tagged_sents):
        """
        n -- order of the model.
        tagged_sents -- list of sentences, each one being a list of pairs.
        """
        self._n = n
        self._words = set()

        # Determine the vocabulary.
        for tagged_sent in tagged_sents:
            for tup in tagged_sent:
                self._words.add(tup[0])

        basic_features = [word_lower, word_istitle, word_isupper, word_isdigit]

        features = basic_features + \
            [PrevWord(feature) for feature in basic_features] + \
            [NPrevTags(i+1) for i in range(self._n-1)]

        self._pipeline = Pipeline([('vect', Vectorizer(features=features)),
                                   ('classifier', LogisticRegression())])

        histories = self.sents_histories(tagged_sents)
        tags = self.sents_tags(tagged_sents)
        self._pipeline.fit(histories, tags)

    def sents_histories(self, tagged_sents):
        """Iterator over the histories of a corpus.

        tagged_sents -- the corpus (a list of sentences)
        """
        ret = []

        for tagged_sent in tagged_sents:
            ret += self.sent_histories(tagged_sent)

        return ret

    def sent_histories(self, tagged_sent):
        """Iterator over the histories of a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """

        tags = (self._n-1)*['<s>']
        sent = []
        for (word, tag) in tagged_sent:
            sent.append(word)
            tags.append(tag)

        return (History(sent, tuple(tags[i:i+self._n-1]), i) for
                i in range(len(tagged_sent)))

    def sents_tags(self, tagged_sents):
        """
        Iterator over the tags of a corpus.

        tagged_sents -- the corpus (a list of sentences)
        """
        ret = []

        for t_sent in tagged_sents:
            ret += self.sent_tags(t_sent)

        return ret

    def sent_tags(self, tagged_sent):
        """Iterator over the tags of a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """

        return (tup[1] for tup in tagged_sent)

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """
        # Beam inference with beam's size == 1.
        ret = []
        tags = (self._n-1)*('<s>',)
        for i in range(len(sent)):
            tag = self.tag_history(History(sent, tags, i))
            ret.append(tag)

            # Tags for the history of the next iteration.
            tags = tags[1:] + (tag,)

        return ret

    def tag_history(self, h):
        """Tag a history.

        h -- the history.
        """
        return self._pipeline.predict([h])[0]

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return w not in self._words
