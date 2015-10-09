"""Print corpus statistics.
Usage:
  stats.py
  stats.py -h | --help
Options:
  -h --help     Show this screen.
"""
from docopt import docopt
from collections import defaultdict

import sys
# TODO: resolver esto!
sys.path.append("/home/mallku/Desktop/PLN/Prácticos/Mi Repo Git/PLN-2015/")

from corpus.ancora import SimpleAncoraCorpusReader

def calculate_counts(sents):
    # Collect data about the corpus.
    words_occurrences = 0
    words = set()
    tags = set()
    dict_tags_count = defaultdict(int)
    words_per_tags = {}
    tags_per_words = {}
    tags_statistics = {}
    amb_statistics = {}
    
    for sent in sents:
        # Each element in sent is a tuple, corresponding to a tagged word.
        len_sent = len(sent)
        words_occurrences += len_sent
        for i in range(len_sent):
            tup = sent[i]
            word, tag = tup[0], tup[1]
            words.add(word)
            tags.add(tag)
            
            if tag not in words_per_tags:
                words_per_tags[tag] = defaultdict(int)
            words_per_tags[tag][word] += 1
            
            dict_tags_count[tag] += 1
            
            if word not in tags_per_words:
                tags_per_words[word] = defaultdict(int)
                
            tags_per_words[word][tag] += 1

    return (len(sents), words_occurrences, len(words), len(tags),\
            dict_tags_count, words_per_tags, tags_per_words)

def collect_statistics(dict_tags_count, words_per_tags, tags_per_words,\
                       most_seen_tags = 10, words_with_tag = 5):
    # Sort dicts by count.
    def sort_func(tup): return len(tup[1])
    
    tags_count = list(dict_tags_count.items())
    tags_count.sort(reverse = True, key = lambda tup : tup[1])
    
    words_per_tags_counts = list(words_per_tags.items())
    words_per_tags_counts.sort(key = sort_func)

    tags_per_words_counts = list(tags_per_words.items())
    tags_per_words_counts.sort(key = sort_func)
    tags_statistics = {}
    amb_statistics = {}
    # Take the most_seen_tags most seen tags.
    for tag, count in tags_count[0:most_seen_tags]:
        tags_statistics[tag] = {}
        tags_statistics[tag]["count"] = count
        tags_statistics[tag]["total_percent"] = count/float(words_occurrences)

        words_counts = list(words_per_tags[tag].items())
        words_counts.sort(reverse = True, key = lambda tup : tup[1])
        tags_statistics[tag]["words_with_tag"] = words_counts[0: words_with_tag]

    # Statistics about words' ambiguity.
    prev_amb_level = 0
    amb_level = 0
    for word, t_counts in tags_per_words_counts:
        prev_amb_level = amb_level
        amb_level = len(t_counts)
        
        if prev_amb_level != amb_level and prev_amb_level != 0:
            # Sort data about the previous level of ambiguity.
            amb_statistics[prev_amb_level]["words_freq"].sort(reverse = True, key = lambda tup : tup[1])
            if len(amb_statistics[prev_amb_level]["words_freq"]) > 5:
                amb_statistics[prev_amb_level]["words_freq"] = amb_statistics[prev_amb_level]["words_freq"][0:5]

        word_freq = sum(count for count in t_counts.values())
        
        if amb_level not in amb_statistics:
            amb_statistics[amb_level] = {}
            amb_statistics[amb_level]["words"] = 1
            amb_statistics[amb_level]["words_freq"] = []
            amb_statistics[amb_level]["words_freq"].append((word, word_freq))
        else:
            # {amb_level in amb_statistics}
            amb_statistics[amb_level]["words"] += 1
            amb_statistics[amb_level]["words_freq"].append((word, word_freq))

    return (tags_statistics, amb_statistics)

if __name__ == '__main__':
    opts = docopt(__doc__)
    
    # Load the data.
    corpus = SimpleAncoraCorpusReader('ancora-2.0/')
    # TODO: vamos a necesitar todos los valores. Los pasamos a una lista.
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
    tags_statistics, amb_statistics = collect_statistics(dict_tags_count, \
                                                         words_per_tags, \
                                                         tags_per_words)

    # Show statistics.
    print('Estadísticas básicas:')
    print('\tCantidad de oraciones: {}'.format(len_sents))
    print('\tCantidad de ocurrencias de palabras: {}'.format(words_occurrences))
    print('\tCantidad de palabras: {}'.format(len_words))
    print('\tCantidad de etiquetas: {}'.format(len_tags))
    
    print('Etiquetas más frecuentes:')
    
    for tag, data in tags_statistics.items():
        print('Etiqueta: {}'.format(tag))
        print('Frecuencia: {}'.format(data["count"]))
        print('Porcentaje del total: {}'.format(data["total_percent"]))
        print('Palabras más frecuentes: {}'.format(str(data["words_with_tag"])))
        print('-----------------------------')
    
    print('Niveles de ambüedad de las palabras:')
    
    for amb_level, counts in amb_statistics.items():
        print("Nivel de ambigüedad: "+str(amb_level))
        print("Cantidad de palabras: "+str(amb_statistics[amb_level]['words']))
        print("Palabras más frecuentes: "+str(amb_statistics[amb_level]['words_freq']))
        print("-----------------------------")
