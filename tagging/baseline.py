from collections import defaultdict
# TODO: para que uso stats?
from tagging.scripts import stats


class BaselineTagger:

    def __init__(self, tagged_sents):
        """ tagged_sents -- a non-empty list of training sentences, each one being
                        a list of pairs.
        """
        # TODO: estaria bueno poder reutilizar el código de stats?
        self.tags_per_words = {}
        self.most_seen_tag = None
        # TODO: para que uso count?
        count = float('-inf')
        tags_counts = defaultdict(int)

        for sentence in tagged_sents:
            for tuple in sentence:
                word = tuple[0]
                tag = tuple[1]
                if word not in tagged_sents:
                    self.tags_per_words[word] = defaultdict(int)

                # {word into tagged_sents}
                self.tags_per_words[word][tag] += 1
                tags_counts[tag] += 1

        # Determine the most seen tag.
        tags_counts_ordered = list(tags_counts.items())
        tags_counts_ordered.sort(reverse=True,
                                 key=lambda tup: tup[1])

        self.most_seen_tag = tags_counts_ordered[0][0]

        # Order tags by occurrence.
        for word, tags in self.tags_per_words.items():
            self.tags_per_words[word] = list(tags.items())
            self.tags_per_words[word].sort(reverse=True,
                                           key=lambda tup: tup[1])

        print("self.tags_per_words: "+str(self.tags_per_words))

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """
        return [self.tag_word(w) for w in sent]

    def tag_word(self, w):
        """Tag a word.

        w -- the word.
        """
        tag = None

        if not self.unknown(w):
            tag = self.tags_per_words[w][0][0]
        else:
            tag = self.most_seen_tag

        return tag

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return w not in self.tags_per_words
