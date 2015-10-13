from math import log2
from collections import defaultdict

class HMM:
    beginning_symbol = ['<s>']
    stop_symbol = ['</s>']
    
    # TODO: es un modelo de trigrama? 
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
        # TODO: asi?
        ret = 0.0
        
        if prev_tags in self._trans and tag in self._trans[prev_tags]:
            ret = self._trans[prev_tags][tag]
            
        return ret
 
    def out_prob(self, word, tag):
        """Probability of a word given a tag.
 
        word -- the word.
        tag -- the tag.
        """
        # TODO: asi?
        
        ret = 0.0
        
        if tag in self._out and word in self._out[tag]:
            ret = self._out[tag][word]
            
        return ret
 
    def tag_prob(self, y):
        """
        Probability of a tagging.
        Warning: subject to underflow problems.
 
        y -- tagging.
        """
        # TODO: corregir: estamos iterando sobre y en vez de y_extended
        context = tuple(2*HMM.beginning_symbol)
        y_extended = y + HMM.stop_symbol
        prob = 1.0

        # INV : {context has the probability context for the actual tag}
        for tag in y:
            prob *= self.trans_prob(tag, context)
            context = (context[1], tag)
            
        return prob
 
    def prob(self, x, y):
        """
        Joint probability of a sentence and its tagging.
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
        """
        Log-probability of a tagging.
 
        y -- tagging.
        """
        return log2(self.tag_prob(y))
 
    def log_prob(self, x, y):
        """
        Joint log-probability of a sentence and its tagging.
 
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
        self._pi[0] = {}
        # TODO: por que usamos probabilidades logaritmicas?
        self._pi[0][tuple((self._hmm._n-1)*HMM.beginning_symbol)] = (log2(1.0),\
                                                                     [])
        
        # Sets with tags.
        s_k = []
        
        for i in range(self._hmm._n - 1):
            s_k.append(set(HMM.beginning_symbol))
        
        s_k.append(self._hmm.tagset())
        
        n = len(sent)
        
        for k in range(1, n+1):
            self._pi[k] = {}
            
            # Construct every possible tuple with tags from each set in s_k[1:].
            res = [()]
            for s_k_j in s_k[1:]:
                res = [x + (y,) for x in res for y in s_k_j]
            
            for tup in res:
                # Each tuple has length self._hmm._n - 1.
                max_prob = float('-inf')
                tag_max_prob = None
                v = tup[self._hmm._n - 1 - 1]
                u = tup[0: self._hmm._n - 1 - 1]
                # Set the dynamic table.
                for w in s_k[0]:
                    p_context = (w,) + u
                    t_prob = self._hmm.trans_prob(v, p_context)
                    o_prob = self._hmm.out_prob(sent[k-1], v)

                    if t_prob > 0 and o_prob > 0 and p_context in self._pi[k-1]:
                        prob = self._pi[k-1][p_context][0] + \
                                    log2(t_prob) + log2(o_prob)
        
                        if max_prob < prob:
                            max_prob = prob
                            tag_max_prob = w
                
                if tag_max_prob is not None:
                    # Set the max. prob. found, and extend the best tagging
                    # seen so far, with the best tag found.
                    self._pi[k][u + (v,)] = (max_prob, \
                                self._pi[k-1][(tag_max_prob,)  + u][1] + [v])

            # Update sets.
            for i in range(self._hmm._n - 1 + 1 - 1):
                s_k[i] = s_k[i+1]
                
            s_k[self._hmm._n - 1] = self._hmm.tagset()
        
        # Extract the best tagging.
        max_prob = float('-inf')
        max_tag = None
        
        for context in self._pi[n]:
            prob = self._pi[n][context][0]+\
                    log2(self._hmm.trans_prob(HMM.stop_symbol[0], context))

            if max_prob < prob:
                max_prob = prob
                max_tag = self._pi[n][context][1]

        return max_tag

class MLHMM:
 
    def __init__(self, n, tagged_sents, addone=True):
        """
        n -- order of the model.
        tagged_sents -- training sentences, each one being a list of pairs.
        addone -- whether to use addone smoothing (default: True).
        """
        self._n = n
        self._tags_counts = defaultdict(int)
        self._tagged_words_counts = defaultdict(int) 
        self._tagsset = set()
        self._words = set()
        self._len_words = 0.0
        self._addone = addone
        self._tagger = ViterbiTagger(self)

        for sent in tagged_sents:
            # Count of tags.
            tags = [x[1] for x in sent]
            
            # TODO: realizamos el mismo conteo que en Interpolation. Quizas
            # necesite directamente tener un objeto Interpolation para modelar
            # el lenguaje de las etiquetas. De todos modos, los tests
            # me funcionan, sin utilizar interpolacion, pero sí habiendo
            # realizado los conteos que se corresponden con interpolacion.
            for j in range(1, n+1):
                tags_extended = j*HMM.beginning_symbol + tags + HMM.stop_symbol
                for i in range(len(tags_extended) - j + 1):
                    ngram = tuple(tags_extended[i: i + j])
                    self._tags_counts[ngram] += 1
                    
                    if j == 1:
                        self._tags_counts[()] += 1
                        self._tagsset.add(tags_extended[i])
                
                if j == 1:
                    # Subtract the symbol <s>.
                    self._tags_counts[()] -= 1

            # TODO: para cualquier valor de n, solo nos interesa P(word|tag)?.
            # La interfaz de out_prob sugiere que si.
            # Count of tagged words.
            for tagged_word in sent:
                self._tagged_words_counts[tagged_word] += 1
                self._words.add(tagged_word[0])
        self._len_words = len(self._words)

    def tcount(self, tokens):
        """Count for an k-gram for k <= n.
 
        tokens -- the k-gram tuple.
        """
        return self._tags_counts[tokens]

    def unknown(self, w):
        """Check if a word is unknown for the model.
 
        w -- the word.
        """
        return w not in self._words
        
    def tagset(self):
        """Returns the set of tags.
        """
        return self._tagsset
 
    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.
 
        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        ret = 0.0
        
        if self._addone:
            ret = (self._tags_counts[prev_tags + (tag,)] + 1.0) / \
                (self._tags_counts[prev_tags] + self._tags_counts[()])
        else:
            # {not self._addone}
            if prev_tags in self._tags_counts:
                ret = self._tags_counts[prev_tags + (tag,)] / \
                    float(self._tags_counts[prev_tags])
 
        return ret

    def out_prob(self, word, tag):
        """Probability of a word given a tag.
 
        word -- the word.
        tag -- the tag.
        """
        ret = 0.0

        if self.unknown(word):
            ret = 1.0/self._len_words
        else:
            # {not self.unknown(word)}
            ret = self._tagged_words_counts[(word, tag)] / float(self._tags_counts[(tag,)])

        return ret
 
    def tag_prob(self, y):
        """
        Probability of a tagging.
        Warning: subject to underflow problems.
 
        y -- tagging.
        """
        context = tuple((self._n-1)*HMM.beginning_symbol)
        y_extended = tuple(y + HMM.stop_symbol)
        prob = 1.0

        # INV : {context has the probability context for the actual tag}
        for tag in y_extended:
            prob *= self.trans_prob(tag, context)
            # TODO: no hay una abstracción más elegante?
            if self._n > 1:
                context = context[1:]  + (tag,)
            
        return prob
 
    def prob(self, x, y):
        """
        Joint probability of a sentence and its tagging.
        Warning: subject to underflow problems.
 
        x -- sentence.
        y -- tagging.
        """
        # TODO: estoy copiando y pegando el mismo código de HMM...
        o_prob = 1.0
        tagging_prob = self.tag_prob(y)
        
        i = 0
        for i in range(len(x)):
            o_prob *= self.out_prob(x[i], y[i])
            
        return tagging_prob*o_prob
 
    def tag_log_prob(self, y):
        """
        Log-probability of a tagging.
 
        y -- tagging.
        """
        context = tuple((self._n-1)*HMM.beginning_symbol)
        y_extended = tuple(y + HMM.stop_symbol)
        prob = 0.0

        # INV : {context has the probability context for the actual tag}
        for tag in y_extended:
            prob += log2(self.trans_prob(tag, context))
            # TODO: no hay una abstracción más elegante?
            if self._n > 1:
                context = context[1:]  + (tag,)

        return prob
 
    def log_prob(self, x, y):
        """
        Joint log-probability of a sentence and its tagging.
 
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
        
        return self._tagger.tag(sent)
        