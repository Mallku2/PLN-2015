# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from random import random, randrange

# TODO: por que log2?
from math import log2, floor
# TODO: correr este codigo con la herramienta de verificacion de codigo
# TODO: asi esta bien?
begin = ['<s>']
end = ['</s>']

# TODO: quizas sea mejor definir un procedimiento en vez de una clase
class DataSet(object):
    def __init__(self, sents):
        self.sents = sents
        self.len_sents = len(sents)
        
    def __arrange_sub_set(self, min_index_data, max_index_data, length_data):
        """ Selects, in place, a random subset of values of cardinal length_data, 
            searching between min_index_data and max_index_data. Stores the 
            results between min_index_data and length_data+min_index_data-1.
            
            max_index_data : the last index in self.sents.
            min_index_data : the first index in self.sents.
            length_data : quantity of values to select.
        """
        swap_pos = max_index_data # Position into dict where we store the selected sents. 
        for i in range(length_data + 1):
            pos = floor(random()*(swap_pos+1)) # 0 <= pos <= swap_pos
            aux = self.sents[swap_pos]
            self.sents[swap_pos] = self.sents[pos]
            self.sents[pos] = aux
            swap_pos -= 1
    
    def extract_sets(self, l_training_set = 0.8, l_held_out_set = 0.1, \
                     l_test_set = 0.1):
        """ Divides the data set into training, test and held out data.
            Returns a triple (training set list, held out set list, test set 
            list).
            
            l_training_set : proportion from the whole data set used as training 
                            data.
            l_held_out_set : proportion from the whole data set used as held out 
                            data.
            l_test_set : proportion from the whole data set used as test data.
            
            PRE : { the parameters are proportion values &&
                    l_training_set + l_held_out_set + l_test_set == 1.0 }
        """
        
        test_set_length = floor(l_test_set*self.len_sents)
        training_set_length = floor(l_training_set*self.len_sents)
        held_out_set_length = floor(l_held_out_set*self.len_sents)
        
        self.__arrange_sub_set(0, self.lent_sents, training_set_length)
        self.__arrange_sub_set(training_set_length, self.lent_sents, held_out_set_length)
        self.__arrange_sub_set(training_set_length + held_out_set_length + 1, \
                               self.lent_sents, test_set_length)
        
        return (self.sents[0, training_set_length], \
                self.sents[training_set_length, training_set_length + held_out_set_length + 1],\
                self.sents[training_set_length + held_out_set_length + 1, self.len_sents])
        

class NGram(object):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        # self.sents = sents
        # words = {}
        # TODO: que significa esta construccion?
        # Counts of every n and n-1-gram (used as contexts) seen in the corpus.
        self.counts = counts = defaultdict(int)
        self.contexts = dict()
        for sent in sents:
            # TODO: libro de Jurafsky, página 103, leer nota de la figura 4.3:
            # todas las letras del corpus en minuscula, simbolos de puntuacion
            # tratados como palabras. Por qué?
            # For n > 1, we need the starting, for the n-gram context of
            # the first word of each sentence.
            # TODO: por que necesitamos end? (ver libro, pagina 99)
            sent = begin*(n-1) + sent + end
            # Notar que los ultimos ngram tienen longitud menguante,
            # a partir del momento en el que i+n > len(sent), por lo tanto,
            # hacemos que i vaya hasta len(sent) - n.
            for i in range(len(sent) - n + 1):
                # Construye todos los n-gramas posibles,
                # comenzando en (0,n-1), (1, n), etc...
                # Notar que con estos indices, siempre el primer n-grama
                # consiste en la repeticion del simbolo begin, n veces. De ahi
                # en adelante, se va retirando un simbolo begin de la izq, y se
                # agrega una nueva palabra a la derecha.
                ngram = tuple(sent[i: i + n])
                # Contabiliza al n-grama
                counts[ngram] += 1
                # Contabiliza al (n-1)-grama: va desde 0 hasta el ante-último
                # elemento
                counts[ngram[:-1]] += 1
                if not ngram[:-1] in self.contexts:
                    self.contexts[ngram[:-1]] = list()

                if not ngram[n-1] in self.contexts[ngram[:-1]]:
                    self.contexts[ngram[:-1]].append(ngram[n-1])


    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.
 
        tokens -- the n-gram or (n-1)-gram tuple.
        """
        # TODO: tokens puede ser un string o una tupla?
        # TODO: recordar reemplazar el uso de self.counts por la llamada
        # a este metodo.
        return self.counts[tokens]
 
    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        # TODO: prev_tokens es una lista!
        assert prev_tokens != None or self.n == 1
        if prev_tokens == None:
            # {n == 1}
            ret = float(self.counts[tuple([token])]) / self.counts[()]
        else:
            # {prev_tokens != None}
            tokens = prev_tokens + [token]
            if self.counts[tuple(prev_tokens)] != 0:
                # MLE approximation of the probability P(token | prev_tokens)
                ret = self.counts[tuple(tokens)] / float(self.counts[tuple(prev_tokens)])
            else:
                # {self.counts[tuple(prev_tokens)] == 0}
                ret = 0.0
            
        return ret 
 
    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.
 
        sent -- the sentence as a list of tokens.
        """
        
        # TODO: leer las notas de MyS 2014 sobre calculo numerico con Python,
        # para evitar los problemas de underflow
        
        prob = 1.0
        
        # To make sent_prob a real probability distribution, we add the end-symbol.
        sent = sent + end
        if self.n > 1:
            # We add a beginning symbol to complete the n-gram context for the
            # first n words.
            sent = begin*(self.n-1) + sent
            
        for i in range(self.n-1, len(sent)):
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[n-i] hasta 
            # i-1).
            if self.n == 1:
                prob *= self.cond_prob(sent[i])
            else:
                # {self.n > 1}
                # To avoid P(<s>|?)
                if i > 0:
                    prob *= self.cond_prob(sent[i], sent[i-(self.n-1):i])
            
        return prob
 
    def sent_log_prob(self, sent):
        """Log-probability of a sentence.
 
        sent -- the sentence as a list of tokens.
        """
        # TODO: leer las notas de MyS 2014 sobre calculo numerico con Python,
        # para evitar los problemas de underflow
        
        log_prob = 0.0
        
        # To make sent_prob a real probability distribution, we add the 
        # end-symbol.
        sent = sent + end
        if self.n > 1:
            # We add a beginning symbol to complete the n-gram context for the
            # first n words.
            sent = begin*(self.n-1) + sent
            
        for i in range(self.n-1, len(sent)):
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[i-(n-1)] hasta 
            # i-1).
            if self.n == 1:
                prob = self.cond_prob(sent[i])
                if prob > 0:
                    log_prob += log2(prob)
                else:
                    log_prob = float("-inf")
                    break
            else:
                # {self.n > 1}
                # To avoid P(<s>|?)
                if i > 0:
                    prob = self.cond_prob(sent[i], sent[i-(self.n-1):i])
                    if prob > 0:
                        log_prob += log2(prob)
                    else:
                        log_prob = float("-inf")
                        break
            
        return log_prob
        
class NGramGenerator:
 
    def __init__(self, model):
        """
        model -- n-gram model.
        """
        """self.ngram_model = model
        # TODO: parece que probs es algo de la forma {Contexto de n-grama X {palabraXprob}}
        self.probs = dict()
        self.sorted_probs = dict()
        for key in self.ngram_model.counts.keys():
            if len(key) == self.ngram_model.n-1:
                # key es un n-1-grama
                self.probs[key] = dict()
                self.sorted_probs[key] = list()
                for gram in self.ngram_model.counts.keys():
                    if len(gram) == self.ngram_model.n and key == gram[:-1]:
                        # gram begins with key.
                        word = gram[len(gram)-1]
                        if self.ngram_model.n > 1:
                            self.probs[key][word] = self.ngram_model.cond_prob(word, list(key))
                        else:
                            self.probs[key][word] = self.ngram_model.cond_prob(word)
                        
                        self.sorted_probs[key].append((word, self.probs[key][word]))
                self.sorted_probs[key].sort(key=lambda x: x[1])
                self.sorted_probs[key].sort(key=lambda x: x[0])"""
        self.ngram_model = model
        # TODO: parece que probs es algo de la forma {Contexto de n-grama X {palabraXprob}}
        # TODO: preguntar si es correcto definir en NGram estos contextos
        self.probs = dict()
        self.sorted_probs = dict()
        for key in self.ngram_model.contexts.keys():
            self.probs[key] = dict()
            self.sorted_probs[key] = list()
            for word in self.ngram_model.contexts[key]:
                if self.ngram_model.n > 1:
                    self.probs[key][word] = self.ngram_model.cond_prob(word, list(key))
                else:
                    self.probs[key][word] = self.ngram_model.cond_prob(word)
                
                self.sorted_probs[key].append((word, self.probs[key][word]))
            self.sorted_probs[key].sort(key=lambda x: x[1])
            self.sorted_probs[key].sort(key=lambda x: x[0])
 
    def generate_sent(self):
        """Randomly generate a sentence."""
        # Construct the ngram context for the first word
        prev_tokens = (self.ngram_model.n-1)*begin
        sent = []
        
        word = self.generate_token(tuple(prev_tokens))
        while word != end[0]:
            sent.append(word)
            if self.ngram_model.n > 1:
                prev_tokens = prev_tokens[1:] + [word]
            word = self.generate_token(tuple(prev_tokens))
        
        return sent
        
    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.
 
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        generated_token = None
        if prev_tokens != None:
            gram = prev_tokens
        else:
            # {prev_tokens == None}
            gram = ()
            
        # Select a position.
        u = random()
        prob_acum = 0.0
        # Determine the interval to which u belongs.
        for word, prob in self.sorted_probs[prev_tokens]:
            prob_acum += prob
            if u <= prob_acum:
                generated_token = word
                break
            
        assert(generated_token != None)
        
        return generated_token
    
class AddOneNGram:
 
    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        # TODO: cambiar list por una estructura de datos sobre la que sea eficiente
        # el test de pertenecencia de un elemento.
        self.words = list()
        self.lenWords = 0
        #words = {}
        # TODO: que significa esta construccion?
        # Counts of every n and n-1-gram (used as contexts) seen in the corpus.
        self.counts = counts = defaultdict(int)
        self.contexts = dict()
        # TODO: parece que aqui no es necesario colocar estos marcadores. Los 
        # tests de ngramas me funcionan. Observando los tests del generador
        # de oraciones, parece que tengo que lograr que el simbolo de final
        # sea interpretado como un unico caracter, cosa que no sucede, si lo
        # agrego ahora. Solucion: colocarlos dentro de una tupla
        #sents = sents+[end]
        for sent in sents:
            # For n > 1, we need the starting, for the n-gram context of
            # the first word of each sentence.
            # TODO: por que necesitamos end? (ver libro, pagina 99)
            sent = begin*(n-1) + sent + end
            # Notar que los ultimos ngram tienen longitud menguante, 
            # a partir del momento en el que i+n > len(sent), por lo tanto,
            # hacemos que i vaya hasta len(sent) - n.
            for i in range(len(sent) - n + 1):
                # TODO: aca estoy agregando tambien el simbolo de comienzo.
                if not sent[i] in self.words:
                    self.words.append(sent[i])
                    self.lenWords += 1
                
                ngram = tuple(sent[i: i + n])
                # Contabiliza al n-grama
                counts[ngram] += 1
                # Contabiliza al (n-1)-grama: va desde 0 hasta el ante-último
                # elemento
                counts[ngram[:-1]] += 1
                if not ngram[:-1] in self.contexts:
                    self.contexts[ngram[:-1]] = list()
                
                if not ngram[n-1] in  self.contexts[ngram[:-1]]:
                    self.contexts[ngram[:-1]].append(ngram[n-1])
                    
            # Add the remaining words in sent:
            for i in range(len(sent) - n + 1, len(sent)):
                if not sent[i] in self.words:
                    self.words.append(sent[i])
                    self.lenWords += 1
        
        # Substract 1 to self.lenWords, for the beginning symbol.
        if self.n > 1:
            self.lenWords -= 1
            
    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.
 
        tokens -- the n-gram or (n-1)-gram tuple.
        """
        # TODO: tokens puede ser un string o una tupla?
        return self.counts[tokens]
 
    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        # TODO: prev_tokens es una lista!
        assert prev_tokens != None or self.n == 1
        if prev_tokens == None:
            # {n == 1}
            # TODO: notar que en el libro de Jurafsky propone modificar solo el
            # numerador (pagina 109 del pdf).
            ret = float(self.counts[tuple([token])] + 1) / (self.counts[()] + \
                                                        self.lenWords)
        else:
            # {prev_tokens != None}
            # TODO: estoy construyendo una nueva lista ([token]) para sumarsela
            # a la otra. Deberia usar append. Usar flake8 para revisar codigo
            # Debe ser pep8
            tokens = prev_tokens + [token]
            """if self.counts[tuple(prev_tokens)] != 0:
                # MLE approximation of the probability P(token | prev_tokens)
                ret = float(self.counts[tuple(tokens)] + 1) / (self.counts[tuple(prev_tokens)] +\
                                                            self.lenWords)
            else:
                # {self.counts[tuple(prev_tokens)] == 0}
                ret = 0.0"""
            # TODO: en Addone sabemos que el numerador siempre va a ser >= a 1
            # y el denominador >= a self.lenWords, por lo tanto, no necesitamos
            # realizar el chequeo anterior.
            ret = float(self.counts[tuple(tokens)] + 1) / (self.counts[tuple(prev_tokens)] +\
                                                            self.lenWords)
            
        return ret 
 
    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.
 
        sent -- the sentence as a list of tokens.
        """
        
        # TODO: los problemas de overflow que puede tener este algoritmo,
        # se solucionan en sent_log_prob
        prob = 0.0
        
        # To make sent_prob a real probability distribution, we add the end-symbol.
        sent = sent + end
        if self.n > 1:
            # We add a beginning symbol to complete the n-gram context for the
            # first n words.
            sent = begin*(self.n-1) + sent
            
        for i in range(self.n-1, len(sent)):
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[n-i] hasta 
            # i-1).
            if self.n == 1:
                prob *= self.cond_prob(sent[i])
            else:
                # {self.n > 1}
                # To avoid P(<s>|?)
                if i > 0:
                    prob *= self.cond_prob(sent[i], sent[i-(self.n-1):i])
            
        return prob
 
    def sent_log_prob(self, sent):
        """Log-probability of a sentence.
 
        sent -- the sentence as a list of tokens.
        """
        # TODO: leer las notas de MyS 2014 sobre calculo numerico con Python,
        # para evitar los problemas de underflow
        
        log_prob = 0.0
        
        # To make sent_prob a real probability distribution, we add the 
        # end-symbol.
        sent = sent + end
        if self.n > 1:
            # We add a beginning symbol to complete the n-gram context for the
            # first n words.
            sent = begin*(self.n-1) + sent
            
        for i in range(self.n-1, len(sent)):
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[i-(n-1)] hasta 
            # i-1).
            if self.n == 1:
                prob = self.cond_prob(sent[i])
                """if prob > 0:
                    log_prob += log2(prob)
                else:
                    log_prob = float("-inf")
                    break"""
                # TODO: en addone, siempre prob>0
                log_prob += log2(prob)
            else:
                # {self.n > 1}
                # To avoid P(<s>|?)
                if i > 0:
                    prob = self.cond_prob(sent[i], sent[i-(self.n-1):i])
                    """if prob > 0:
                        log_prob += log2(prob)
                    else:
                        log_prob = float("-inf")
                        break"""
                    log_prob += log2(prob)
            
        return log_prob
 
    def V(self):
        """Size of the vocabulary.
        """
        return self.lenWords
    
# TODO: preguntas: * de donde obtengo los datos held-out? de la lista sents
# recibida como parametro?
#                * como se implementaria el algoritmo de barrido para
# determinar el valor de gamma?

# TODO: si la bandera addone esta en true, no importa el valor de n, solo cuando nos 
# toque trabajar con el modelo de unigrama, utilizar siempre interpolacion. Si
# la bandera addone esta en false, entonces nada.

# TODO: el valor de gamma depende del corpus sobre el que estoy entrenando.
# Mientras mas grande el parametro gamma, menores seran los lambdas. Cuando mas
# agrande el gamma, menos peso le dare a los modelos para n mayores, mas peso
# le dare a los lambdas mayores.

# TODO: al crear los objeto NGram, estamos repitiendo el conteo de ciertos
# n-gramas: el objeto NGram(n,...) contabiliza n-gramas y n-1-gramas. El objeto
# NGram(n-1,...), contabilizar n-1-gramas y n-2-gramas, etc. Es mejor realizar
# nosotros el conteo en la clase InterpolatedNGram: metodo de ayuda: update.
class InterpolatedNGram:
 
    def __init__(self, n, sents, gamma=None, addone=True):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        gamma -- interpolation hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        self.n = n
        # TODO: re-implementar esto usando sets
        self.words = []
        self.lenWords = 0
        self.addone = addone
        
        # TODO: por ahora, desconozco el parametro addone. En la documentacion
        # del practico indica que se debe usar addone para el modelo de unigrama.
        # Pero entonces, para que tenemos el parametro addone?
        self.counts = defaultdict(int)
        
        if not gamma:
            # TODO: self.held_out_set como lo determino?. Los tests de Franco
            # piden una forma determinista de construirlo...
            len_sents = len(sents)
            self.training_set = sents[0:floor(0.9*len_sents)-1]
            self.held_out_set = sents[floor(0.9*len_sents):floor(0.9*len_sents)+floor(0.1*len_sents)-1]
            #(self.training_set, self.held_out_set) = self.__extract_sets(sents)
        else:
            self.training_set = sents
            self.held_out_set = []
        
        for sent in self.training_set:
            # TODO: recordar que para n == 1 tenemos que usar addone.
            sent_completed = begin*(self.n-1) + sent + end
            
            for i in range(len(sent_completed) - self.n + 1):
                # TODO: feo
                if self.addone:
                    if not sent_completed[i] in self.words:
                        self.words.append(sent_completed[i])
                        self.lenWords += 1
                        
                ngram = tuple(sent_completed[i: i + self.n])
                j = self.n
                jgram = ngram
                # Count the ngram and the jgram contexts, for 0 <= j <= self.n-1
                while j >= 0:
                    self.counts[jgram] += 1
                    j -= 1
                    jgram = jgram[self.n-j:]
                    
            if self.addone:
                for i in range(len(sent_completed) - self.n + 1, len(sent_completed)):
                    # TODO: feo
                    if not sent_completed[i] in self.words:
                        self.words.append(sent_completed[i])
                        self.lenWords += 1
                        
        if not gamma:
            self.__estimate_gamma()
        else:
            self.gamma = gamma

    # TODO: para escoger el intervalo de trabajo, vamos a ir viendo a ojo, que
    # intervalo contiene al gamma, de acuerdo a si el valor de perplejidad
    # para el modelo resultante mejora. Asi vamos determinando el intervalo en
    # donde podria caer el valor de gamma adecuado.
    def __estimate_gamma(self):
        """ Hill climbing algorithm to do a local search of a gamma parameter
            that maximizes the perplexity, over the held-out data.
        """
        max = float("-inf")
        # TODO: como no tengo en claro a que se refieren con esto de barrido
        # tomo como ejemplo lo comentado por Alberto en la lista de mails.
        gamma_min = 1
        gamma_max = 1000
        step = 1
        gamma = randrange(gamma_min, gamma_max)
        repeat = True
        l = float("-inf")
        
        # Counts over the development set.
        counts = defaultdict(int)
        
        ngrams = []
        
        for sent in self.held_out_set:
            for i in range(len(sent) - self.n + 1):
                gram = sent[i: i+self.n]
                counts[tuple(gram)] += 1
                ngrams.append(gram)
        
        while repeat:
            print("l: "+str(l))
            print("gamma: "+str(gamma))
            if gamma - step > 0:
                self.gamma = gamma - step
                l_left = self.__log_likelihood(ngrams, counts)
                
                self.gamma = gamma + step
                l_right = self.__log_likelihood(ngrams, counts)

                if l_left > l and l_left >= l_right:
                    gamma = gamma - step
                    l = l_left
                
                elif l_right > l and l_right >= l_left:
                    gamma = gamma + step
                    l = l_right
                    
                elif l >= l_left and l >= l_right:
                    # A (local?) max.
                    repeat = False
                    self.gamma = gamma
            else:
                # {gamma - step <= 0}
                repeat = False
                self.gamma = gamma
    
    def __log_likelihood(self, ngrams, counts_ngrams):
        """ Evaluates the log-likelihood function over the sentences given.
        
            ngrams : a list of ngrams, each one represented as a list of tokens.
            counts_ngrams : a dictionary with the counts of each ngram seen in ngrams.
        """
        L = 0
        for sent in ngrams:
            # TODO: que hacemos cuando c_prob == 0?
            c_prob = self.cond_prob(sent[self.n-1], sent[:-1])
            if c_prob != 0.0:
                L += counts_ngrams[tuple(sent)]*log2(c_prob)
                
        return L
    
    def __calculate_lambda(self, i, prev_tokens, lambdas_prev):
        """
        i : number of lambda (1 <= i <= self.n)
        lambdas_prev : list
        """
        
        sum_lambdas = sum(lambda_j for lambda_j in lambdas_prev)
        
        # TODO: cual es el n del modelo que elijo?
        ret = (1.0 - sum_lambdas)
        if self.n - i > 0:
            count = self.count(tuple(prev_tokens))
            ret *= float(count)/(count + self.gamma)
        
        #print("lambda "+str(i)+": "+str(ret))
        return ret
    
    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.
 
        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts[tokens]
        
    # TODO: recordar de utilizar __ para todos los metodos auxiliares que 
    # estamos incluyendo.
    def __ngram_cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        # TODO: prev_tokens es una lista!
        assert prev_tokens != None or self.n == 1
        if prev_tokens == None:
            # {n == 1}
            if self.addone:
                ret = float(self.count((token,)) + 1) / (self.count(()) + self.lenWords)
            else:
                # {not self.addone}
                ret = float(self.count((token,))) / self.count(())
        else:
            # {prev_tokens != None}
            tokens = prev_tokens + [token]
            count_prev_tokens = self.count(tuple(prev_tokens))
            # TODO: preguntar si esto es correcto!.
            if count_prev_tokens != 0:
                # MLE approximation of the probability P(token | prev_tokens)
                ret = self.count(tuple(tokens)) / float(count_prev_tokens)
            else:
                # {self.counts[tuple(prev_tokens)] == 0}
                ret = 0.0
            
        return ret 

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        ret = 0.0
        lambdas = []
        if prev_tokens == None:
            arg_prev_tokens = []
        else:
            # {prev_tokens != None}
            arg_prev_tokens = prev_tokens
            
        for i in range(1, self.n+1):
            # TODO: cuando un lambda_i da 0, entonces no intento calcular la 
            # cond_prob asociada.
            lambda_i = self.__calculate_lambda(i, arg_prev_tokens, lambdas)
            if lambda_i != 0.0:
                ret += lambda_i*self.__ngram_cond_prob(token, arg_prev_tokens)
            
            lambdas.append(lambda_i)
            arg_prev_tokens = arg_prev_tokens[1:]
        
        return ret

    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.
 
        sent -- the sentence as a list of tokens.
        """
        
        # TODO: leer las notas de MyS 2014 sobre calculo numerico con Python,
        # para evitar los problemas de underflow
        
        prob = 1.0
        
        # To make sent_prob a real probability distribution, we add the end-symbol.
        sent = sent + end
        if self.n > 1:
            # We add a beginning symbol to complete the n-gram context for the
            # first n words.
            sent = begin*(self.n-1) + sent
            
        for i in range(self.n-1, len(sent)):
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[n-i] hasta 
            # i-1).
            if self.n == 1:
                prob *= self.cond_prob(sent[i])
            else:
                # {self.n > 1}
                # To avoid P(<s>|?)
                if i > 0:
                    prob *= self.cond_prob(sent[i], sent[i-(self.n-1):i])
            
        return prob
 
    def sent_log_prob(self, sent):
        """Log-probability of a sentence.
 
        sent -- the sentence as a list of tokens.
        """
        # TODO: leer las notas de MyS 2014 sobre calculo numerico con Python,
        # para evitar los problemas de underflow
        
        log_prob = 0.0
        
        # To make sent_prob a real probability distribution, we add the 
        # end-symbol.
        sent = sent + end
        if self.n > 1:
            # We add a beginning symbol to complete the n-gram context for the
            # first n words.
            sent = begin*(self.n-1) + sent
            
        for i in range(self.n-1, len(sent)):
            # TODO: recordar que tenemos en nuestro modelo símbolos de comienzo
            # y fin de oracion
            # TODO: aqui tenemos que tomar n-1 gramas (desde sent[i-(n-1)] hasta 
            # i-1).
            if self.n == 1:
                prob = self.cond_prob(sent[i])
                if prob > 0:
                    log_prob += log2(prob)
                else:
                    log_prob = float("-inf")
                    break
            else:
                # {self.n > 1}
                # To avoid P(<s>|?)
                if i > 0:
                    prob = self.cond_prob(sent[i], sent[i-(self.n-1):i])
                    if prob > 0:
                        log_prob += log2(prob)
                    else:
                        log_prob = float("-inf")
                        break
            
        return log_prob
    
    def __arrange_sub_set(self, sents, min_index_data, max_index_data, length_data):
        """ Selects, in place, a random subset of values of cardinal length_data, 
            searching between min_index_data and max_index_data. Stores the 
            results between min_index_data and length_data+min_index_data-1.
            
            max_index_data : the last index in self.sents.
            min_index_data : the first index in self.sents.
            length_data : quantity of values to select.
        """
        swap_pos = max_index_data # Position into dict where we store the selected sents. 
        for i in range(length_data + 1):
            pos = floor(random()*(swap_pos+1)) # 0 <= pos <= swap_pos
            aux = sents[swap_pos]
            sents[swap_pos] = sents[pos]
            sents[pos] = aux
            swap_pos -= 1
    
    def __extract_sets(self, sents, l_training_set = 0.9, l_held_out_set = 0.1):
        """ Divides the data set into training and held out data.
            Returns a triple (training set list, held out set list, test set 
            list).
            
            l_training_set : proportion from the whole data set used as training 
                            data.
            l_held_out_set : proportion from the whole data set used as held out 
                            data.
            
            PRE : { the parameters are proportion values &&
                    l_training_set + l_held_out_set == 1.0 }
        """
        len_sents = len(sents)
        training_set_length = floor(l_training_set*len_sents)
        held_out_set_length = floor(l_held_out_set*len_sents)
        
        self.__arrange_sub_set(sents, 0, len_sents-1, training_set_length)
        self.__arrange_sub_set(sents, training_set_length, len_sents-1, \
                               held_out_set_length)
        
        return (sents[0:training_set_length], \
                sents[training_set_length:training_set_length + \
                           held_out_set_length + 1])
        
        
if __name__ == "__main__":
    sents = ['el gato come pescado .'.split(),
            'la gata come salmón .'.split(),]
    
    model = InterpolatedNGram(2, sents, addone=False)
    model.cond_prob('pescado')
    #print("gamma: "+str(model.gamma))
    
    