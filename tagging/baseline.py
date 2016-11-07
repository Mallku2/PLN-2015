from collections import defaultdict


class BaselineTagger:

    def __init__(self, tagged_sents):
        """tagged_sents -- a non-empty list of training sentences, each one
                        being a list of pairs.
        """
        tags_per_words = {}
        self.most_seen_tag_per_words = {}

        tags_counts = defaultdict(int)
        self.most_seen_tag = None

        for sentence in tagged_sents:
            for word, tag in sentence:
                if word not in tags_per_words:
                    tags_per_words[word] = defaultdict(int)

                # {word into tags_per_words}
                tags_per_words[word][tag] += 1

                tags_counts[tag] += 1

        # Order tags by occurrence.
        tags_count_ord = list(tags_counts.items())
        tags_count_ord.sort(reverse=True,
                            key=lambda tup: tup[1])
        self.most_seen_tag = tags_count_ord[0][0]

        # Select the most seen tag, for each word.
        for word, tags in tags_per_words.items():
            tags_per_words[word] = list(tags.items())
            tags_per_words[word].sort(reverse=True,
                                      key=lambda tup: tup[1])
            # Stay with the most seen tag.
            self.most_seen_tag_per_words[word] = tags_per_words[word][0][0]

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
            tag = self.most_seen_tag_per_words[w]
        else:
            tag = self.most_seen_tag

        return tag

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return w not in self.most_seen_tag_per_words
