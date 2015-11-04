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
    """Collects stats. from the corpus:
        _ quantity of sentences.
        _ words.
        _ words' occurrences.
        _ tags.
        _ tags' counts.
        _ for a given word, the count of the tags with which it appears in the
            corpus.
        _ for a given tag, the count of the words with which it appears in the
            corpus.
    """
    # Collect data about the corpus.
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

            words_per_tags[tag][word] += 1

            dict_tags_count[tag] += 1

            if word not in tags_per_words:
                tags_per_words[word] = defaultdict(int)

            tags_per_words[word][tag] += 1

    return len(sents), words_occurrences, len(tags_per_words),\
        len(words_per_tags), dict_tags_count, words_per_tags,\
        tags_per_words


def collect_statistics(dict_tags_count, words_per_tags, tags_per_words,
                       tags_occurrences, most_seen_tags=10,
                       words_with_tag=5):
    # Sort tags' counts.
    tags_count = list(dict_tags_count.items())
    tags_count.sort(reverse=True, key=lambda tup: tup[1])

    # Sort tags per word's dict.
    tags_per_words_counts = list(tags_per_words.items())
    tags_per_words_counts.sort(key=lambda tup: len(tup[1]))

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

    # Statistics about words' ambiguity.
    prev_amb_level = 0
    amb_level = 0

    for word, t_counts in tags_per_words_counts:
        # Calculate the word's ambiguity level.
        prev_amb_level = amb_level
        amb_level = len(t_counts)

        if prev_amb_level != amb_level and prev_amb_level != 0:
            # Sort data about the previous level of ambiguity.
            words_freq = amb_statistics[prev_amb_level]["words_freq"]
            words_freq.sort(reverse=True, key=lambda tup: tup[1])
            if len(words_freq) > 5:
                amb_statistics[prev_amb_level]["words_freq"] = words_freq[:5]

        # Add stats. about a word that occurs with an amb_level level of
        # ambiguity.
        word_freq = sum(count for count in t_counts.values())

        if amb_level not in amb_statistics:
            amb_statistics[amb_level] = {}
            amb_statistics[amb_level]["words"] = 1
            amb_statistics[amb_level]["words_freq"] = [(word, word_freq)]
        else:
            # {amb_level in amb_statistics}
            amb_statistics[amb_level]["words"] += 1
            amb_statistics[amb_level]["words_freq"].append((word, word_freq))

    return (tags_statistics, amb_statistics)


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

    for tag, data in tags_statistics.items():
        tup = data['words_with_tag'][0]
        t, c = tup[0], tup[1]
        freq_words = '\'' + t + '\': ' + str(c)

        # Organize the data related with frequent words and their count.
        for i in range(1, len(data['words_with_tag'])):
            tup = data['words_with_tag'][i]
            t, c = tup[0], tup[1]
            freq_words += ', \'' + t + '\': ' + str(c)

        print(more_freq_template.format(tag, data['count'],
                                        '{:.4}'.format(data['total_percent']),
                                        freq_words))

    # Template for words' ambiguity presentation.
    words_amb_template = '{0:20}|{1:20}|{2:>20}|{3:>20}'

    print('\nNiveles de ambigüedad de las palabras:')

    print('\n'+words_amb_template.format('Nivel de ambigüedad',
                                         'Cantidad de palabras',
                                         'Porcentaje del total',
                                         'Palabras más frecuentes'))

    for amb_level, counts in amb_statistics.items():
        tup = amb_statistics[amb_level]['words_freq'][0]
        t, c = tup[0], tup[1]
        freq_words = '\'' + t + '\': ' + str(c)

        # Organize the data related with frequent words and their count.
        for i in range(1, len(amb_statistics[amb_level]['words_freq'])):
            tup = amb_statistics[amb_level]['words_freq'][i]
            t, c = tup[0], tup[1]
            freq_words += ', \'' + t + '\': ' + str(c)

        quantity = amb_statistics[amb_level]['words']
        print(words_amb_template.format(amb_level,
                                        quantity,
                                        '{:.4}'.format(float(quantity) /
                                                       words_occurrences),
                                        freq_words))
