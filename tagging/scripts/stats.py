"""Print corpus statistics.
Usage:
  stats.py
  stats.py -h | --help
Options:
  -h --help     Show this screen.
"""
from docopt import docopt
from collections import defaultdict

from corpus.ancora import SimpleAncoraCorpusReader


def calculate_counts(sents):
    """Collects basic counts from the list of sentences received.

        PARAMS
        sents : a list of the form [ [ (word, tag) ] ] (where [ (word, tag) ]
                is a tagged sentence represented as a list of tagged words).

        RETURNS
        _quantity of sentences.
        _words' occurrences.
        _words' counts (from every sentence).
        _tags' counts (from every sentence).
        _Dict. of the form {tag X tag's occurences}
        _Dict. of the form {tag X {word X occurrences of word tagged with tag}}
        _Dict. of the form {word X {tag X occurrences of word tagged with tag}}
    """

    words_occurrences = 0
    dict_tags_count = defaultdict(int)
    words_per_tags = {}
    tags_per_words = {}

    for sent in sents:
        len_sent = len(sent)
        words_occurrences += len_sent

        for i in range(len_sent):
            # Each element in sent is a tuple, corresponding to a tagged word.
            tup = sent[i]
            word, tag = tup[0], tup[1]

            if tag not in words_per_tags:
                words_per_tags[tag] = defaultdict(int)

            # {tag in words_per_tags.keys()}
            words_per_tags[tag][word] += 1

            dict_tags_count[tag] += 1

            if word not in tags_per_words:
                tags_per_words[word] = defaultdict(int)

            # {word in tags_per_words.keys()}
            tags_per_words[word][tag] += 1

    return len(sents),\
        words_occurrences,\
        len(tags_per_words),\
        len(words_per_tags),\
        dict_tags_count,\
        words_per_tags,\
        tags_per_words


def collect_statistics(dict_tags_count,
                       words_per_tags,
                       tags_per_words,
                       tags_occurrences,
                       most_seen_tags=10,
                       words_with_tag=5):
    """From the received counts, taken from a given set of sentences,
    calculates frequencies and words' ambiguity levels.

    PARAMS
    _Dict. of the form {tag X tag's occurences}
    _Dict. of the form {tag X {word X occurrences of word tagged with tag}}
    _Dict. of the form {word X {tag X occurrences of word tagged with tag}}
    _Occurrences of tags in the set sentences
    _Quantity of tags for which we want stats (selecting from the most seen
     tag, in decreasing order)
    _Quantity of words to be shown as examples of uses of a given tag

    RETURNS
    _ List., of length most_seen_tags, of the form:
           [(tag,  {"count": ocurrences of tag,
                   "total_percent": percentaje of the occurrence of tag
                   "words_with_tag": list, of length words_with_tag,
                    of the form:
                               [(word, ocurrences of word tagged with tag)]
                    in decreasing order of occurrence.
                  }
             )]
      sorted by value of "count", in increasing order.

    _ Dit. of the form:
           { ambiguity level of words X
                    {"words": quantity of words with the given level of
                              ambiguity,
                     "words_freq": list of the form [(word,
                                                      occurrences of word)]

                    }

           }
    """

    # Sort tags' counts.
    tags_count = list(dict_tags_count.items())
    tags_count.sort(reverse=True, key=lambda tup: tup[1])

    tags_statistics = {}
    amb_statistics = {}

    # Statistics about the most_seen_tags most seen tags.
    for tag, count in tags_count[:most_seen_tags]:
        tags_statistics[tag] = {}
        tags_statistics[tag]["count"] = count
        tags_statistics[tag]["total_percent"] = count/float(tags_occurrences)

        # Select the words_with_tag most frequent words with the given tag.
        words_counts = list(words_per_tags[tag].items())
        words_counts.sort(reverse=True, key=lambda tup: tup[1])
        tags_statistics[tag]["words_with_tag"] = words_counts[: words_with_tag]

    # Sort tags by frequency
    ordered_tag_statistics = list(tags_statistics.items())
    ordered_tag_statistics.sort(key=lambda tup: tup[1]["count"])

    # Statistics about words' ambiguity.
    tags_per_words_counts = list(tags_per_words.items())
    # {tags_per_words_counts is a list of the form
    #  [ ( word, {tag X occurrences of word tagged with the indicated tag} ) ]}

    tags_per_words_counts.sort(key=lambda tup: len(tup[1]))
    # {tags_per_words is ordered by the length of the second component of
    # each tuple, in increasing order}

    # NOTE: the length of the second component of each tuple of
    # tags_per_words_counts represents the ambiguity of the corresponding
    # word.
    prev_amb_level = 0
    amb_level = 0

    # Iterate over the list tags_per_words_counts, in increasing level of
    # word's ambiguity
    for word, t_counts in tags_per_words_counts:
        prev_amb_level = amb_level
        # Obtain the word's ambiguity level.
        amb_level = len(t_counts)

        if prev_amb_level != amb_level and prev_amb_level != 0:
            # New level of ambiguity. Sort data about the previous level of
            # ambiguity.
            amb_statistics[prev_amb_level]["words_freq"] = sort_by_word_freq(
                                amb_statistics[prev_amb_level]["words_freq"],
                                words_with_tag)

        # Occurrences of word.
        word_freq = sum(count for count in t_counts.values())

        if amb_level not in amb_statistics:
            amb_statistics[amb_level] = {}
            amb_statistics[amb_level]["words"] = 0
            amb_statistics[amb_level]["words_freq"] = []

        # {amb_level in amb_statistics}
        amb_statistics[amb_level]["words"] += 1
        amb_statistics[amb_level]["words_freq"].append((word, word_freq))

    # Sort the words of the last ambiguity level considered
    amb_statistics[amb_level]["words_freq"] = sort_by_word_freq(
                                    amb_statistics[amb_level]["words_freq"],
                                    words_with_tag)

    return ordered_tag_statistics, amb_statistics


def sort_by_word_freq(words_freq, length):
    """ Sorts IN PLACE the list of words' occurrences received. The order is
    decreasing. Also truncates the length of the list, according to the
    parameter length.

    PARAMS
    words_freq: list of the form [(word, occurrences of word)]
    length: max length desired for the result
    """
    words_freq.sort(reverse=True, key=lambda tup: tup[1])
    # We only want the first words_with_tag words
    words_freq = words_freq[:length]

    return words_freq

if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/')
    sents = list(corpus.tagged_sents())

    # Collect statistics.
    counts = calculate_counts(sents)
    len_sents = counts[0]
    words_occurrences = counts[1]
    len_words = counts[2]
    len_tags = counts[3]
    dict_tags_count = counts[4]
    words_per_tags = counts[5]
    tags_per_words = counts[6]
    tags_statistics, amb_statistics = collect_statistics(dict_tags_count,
                                                         words_per_tags,
                                                         tags_per_words,
                                                         words_occurrences)

    # Show statistics.
    print('Estadísticas básicas:')
    print('\tCantidad de oraciones: {}'.format(len_sents))
    print('\tCantidad de ocurrencias de palabras: {}'.
          format(words_occurrences))
    print('\tCantidad de palabras: {}'.format(len_words))
    print('\tCantidad de etiquetas: {}'.format(len_tags))

    print('\nEtiquetas más frecuentes:')

    # Template for frequent tags' presentation.
    more_freq_template = '{0:8}|{1:10}|{2:>20}|{3:20}'

    print('\n'+more_freq_template.format('Etiqueta', 'Frecuencia',
                                         'Porcentaje del total',
                                         'Palabras más frecuentes'))

    for tup in tags_statistics:
        # Organize the data related with frequent words and their counts.
        tag = tup[0]
        stats = tup[1]
        freq_words = ''

        for data in stats['words_with_tag']:
            word, count = data[0], data[1]
            freq_words += '\'' + word + '\': ' + str(count) + ', '

        print(more_freq_template.format(tag, stats['count'],
                                        '{:.4}'.format(stats['total_percent']),
                                        freq_words))

    # Template for words' ambiguity presentation.
    words_amb_template = '{0:20}|{1:20}|{2:>20}|{3:>20}'

    print('\nNiveles de ambigüedad de las palabras:')

    print('\n'+words_amb_template.format('Nivel de ambigüedad',
                                         'Cantidad de palabras',
                                         'Porcentaje del total',
                                         'Palabras más frecuentes'))

    for amb_level, counts in amb_statistics.items():
        freq_words = ''
        # Organize the data related with frequent words and their counts.
        for tup in amb_statistics[amb_level]['words_freq']:
            word, count = tup[0], tup[1]
            freq_words += '\'' + word + '\': ' + str(count) + ', '

        quantity = amb_statistics[amb_level]['words']

        print(words_amb_template.format(amb_level,
                                        quantity,
                                        '{:.4}'.format(float(quantity) /
                                                       words_occurrences),
                                        freq_words))
