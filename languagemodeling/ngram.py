# https://docs.python.org/3/library/collections.html
from collections import defaultdict

# TODO: asi esta bien?
begin = tuple("<s>")
end = tuple("</s>")

class NGram(object):
    
    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        
        # TODO: que significa esta construccion?
        
        self.counts = counts = defaultdict(int)
        # TODO: parece que aqui no es necesario colocar estos marcadores. Los 
        # tests de ngramas me funcionan. Observando los tests del generador
        # de oraciones, parece que tengo que lograr que el simbolo de final
        # sea interpretado como un unico caracter, cosa que no sucede, si lo
        # agrego ahora. Solucion: colocarlos dentro de una tupla
        #sents = sents+[end]
        for sent in sents:
            counts[begin] += 1
            counts[end] += 1
            for i in range(len(sent) - n + 1):
                # construye todos los n-gramas posibles, de longitud n,
                # comenzando en (0,n-1), (1, n), etc...
                ngram = tuple(sent[i: i + n])
                # Contabiliza al n-grama
                counts[ngram] += 1
                # Contabiliza al (n-1)-grama: va desde 0 hasta el ante-último
                # elemento
                counts[ngram[:-1]] += 1

    def prob(self, token, prev_tokens=None):
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        # TODO: este assert no es incorrecto para el caso en el que prev_tokens == []?
        assert len(prev_tokens) == n - 1

        tokens = prev_tokens + [token]
        return float(self.counts[tuple(tokens)]) / self.counts[tuple(prev_tokens)]
    
    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.
 
        tokens -- the n-gram or (n-1)-gram tuple.
        """
        
        return self.count[tokens]
 
    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        assert prev_tokens != None or self.n == 1
        # TODO: que devolvemos si prev_tokens == None?
        return float(count(token)) / count(prev_tokens[-self.n+1:])
 
    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.
 
        sent -- the sentence as a list of tokens.
        """
        
        # TODO: leer las notas de MyS 2014 sobre calculo numerico con Python,
        # para evitar los problemas de underflow
        
        prob = 1.0
        for i in range(len(sent)):
            # TODO: que pasa con las condiciones de borde?
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[n-i] hasta 
            # i-1).
            # TODO: tenemos que bajarnos los nuevos tests.
            prob *= cond_prob(sent[i], sent[i-n:i])
            
        return prob
 
    def sent_log_prob(self, sent):
        """Log-probability of a sentence.
 
        sent -- the sentence as a list of tokens.
        """
        # TODO: que es log-probability?
        
class NGramGenerator:
 
    def __init__(self, model):
        """
        model -- n-gram model.
        """
        self.ngram_model = model
        self.probs = dict()
        
        for key in self.ngram_model.counts.keys():
            print("Key: "+str(key))
            if key != ():
                # TODO: que pasa cuando tengo key == ()?
                self.probs[key] = self.ngram_model.prob(key[len(key)-1], key[:-1])
 
    def generate_sent(self):
        """Randomly generate a sentence."""
 
    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.
 
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """