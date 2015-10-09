from math import log2

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
        self._pi[0][tuple(2*HMM.beginning_symbol)] = (log2(1.0), [])
        
        s_k_2 = set(HMM.beginning_symbol)
        s_k_1 = set(HMM.beginning_symbol)
        s_k = self._hmm.tagset()
        
        bp= {}
        
        n = len(sent)
        
        for k in range(1, n+1):
            self._pi[k] = {}
            
            # TODO: aparentemente trabajamos solo sobre los pares de hmm._trans
            for context in self._hmm._trans:
                (u,v) = context
                if u in s_k_1 and v in s_k:
                    max_prob = float('-inf')
                    tag_max_prob = None
    
                    for w in s_k_2:
                        p_context = (w,u)
                        if p_context in self._hmm._trans and \
                        v in self._hmm._trans[p_context]:
                            prob = self._pi[k-1][p_context][0]+\
                                        log2(self._hmm.trans_prob(v, p_context))+\
                                        log2(self._hmm.out_prob(sent[k-1], v))
            
                            if max_prob < prob:
                                max_prob = prob
                                tag_max_prob = w
                    
                    if tag_max_prob is not None:
                        self._pi[k][(u, v)] = (max_prob, \
                                               self._pi[k-1][(tag_max_prob, u)][1] +\
                                               [v])
            
            s_k_2 = s_k_1
            s_k_1 = s_k
            s_k = self._hmm.tagset()
        
        # Extract the best tagging.
        max_prob = float('-inf')
        max_tag = None
        
        for context in self._pi[n]:
            (u, v) = context
            prob = self._pi[n][context][0]+\
                    log2(self._hmm.trans_prob(HMM.stop_symbol[0], context))

            if max_prob < prob:
                max_prob = prob
                max_tag = self._pi[n][context][1]

        return max_tag