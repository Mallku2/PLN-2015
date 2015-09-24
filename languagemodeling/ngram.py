# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from random import random, randrange, uniform

from math import log2, floor, ceil


class NGram(object):

    # Some data about our language model.
    begin = ['<s>']
    end = ['</s>']

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)

        for sent in sents:
            # We add the beginning symbol, repeated for the corresponding
            # n-1-gram context.
            sent_extended = NGram.begin*(n-1) + sent + NGram.end

            for i in range(len(sent_extended) - n + 1):
                ngram = tuple(sent_extended[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """

        return self.counts[tokens]

    def cond_prob(self, token, prev_tokens=None):
        """ Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

        assert prev_tokens is not None or self.n == 1

        if prev_tokens is None:
            # {n == 1}
            ret = float(self.count((token,))) / self.count(())
        else:
            # {prev_tokens is not None}
            tokens = list(prev_tokens)
            tokens.append(token)

            tuple_prev_tokens = tuple(prev_tokens)

            if self.count(tuple_prev_tokens) != 0:
                # MLE approximation of the probability P(token | prev_tokens)
                ret = self.count(tuple(tokens)) / \
                    float(self.count(tuple_prev_tokens))
            else:
                # {self.counts[tuple(prev_tokens)] == 0}
                ret = 0.0

        return ret

    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.

        sent -- the sentence as a list of tokens.
        """

        prob = 1.0

        # We add a beginning symbol to complete the n-1-gram context, for the
        # first n words. To make sent_prob a real probability distribution,
        # we add the end-symbol.
        sent_extended = NGram.begin*(self.n-1) + sent + NGram.end

        for i in range(self.n-1, len(sent_extended)):
            if self.n == 1:
                prob *= self.cond_prob(sent_extended[i])
            else:
                # {self.n > 1}
                prob *= self.cond_prob(sent_extended[i],
                                       sent_extended[i-(self.n-1):i])

        return prob

    def sent_log_prob(self, sent):
        """ Log-probability of a sentence.

        sent -- the sentence as a list of tokens.
        """
        log_prob = 0.0

        sent_extended = NGram.begin*(self.n-1) + sent + NGram.end

        for i in range(self.n-1, len(sent_extended)):
            if self.n == 1:
                prob = self.cond_prob(sent_extended[i])
                if prob > 0:
                    log_prob += log2(prob)
                else:
                    log_prob = float("-inf")
                    break
            else:
                # {self.n > 1}
                prob = self.cond_prob(sent_extended[i],
                                      sent_extended[i-(self.n-1):i])
                if prob > 0:
                    log_prob += log2(prob)
                else:
                    # {prob == 0}
                    log_prob = float("-inf")
                    break

        return log_prob

    def cross_entropy(self, sents, m):
        """ Computes the cross entropy of the model, over a given set of
            sentences.

            sents -- list of sentences, each one being a list of tokens.
            m -- length of sents.
        """
        acum = 0.0
        for sent in sents:
            acum += self.sent_log_prob(sent)

        return (1.0/m)*acum

    def perplexity(self, c_entropy):
        """ Computes the perplexity of the model, over a given set of
            sentences.

            c_entropy -- cross-entropy value.
        """

        return pow(2, -c_entropy)


class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """
        self.ngram_model = model
        self.probs = dict()
        self.sorted_probs = dict()
        n = self.ngram_model.n
        ngrams = set()
        for key in self.ngram_model.counts:
            if len(key) == n:
                ngrams.add(key)

        for key in ngrams:
            context = key[:-1]
            if context not in self.probs:
                self.probs[context] = {}
                self.sorted_probs[context] = list()
            word = key[n-1]
            if n > 1:
                if word not in self.probs[context]:
                    self.probs[context][word] = \
                        self.ngram_model.cond_prob(word, list(context))
                    self.sorted_probs[context].\
                        append((word, self.probs[context][word]))
            else:
                if word not in self.probs[context]:
                    self.probs[context][word] = self.ngram_model.cond_prob(
                        word)
                    self.sorted_probs[context].\
                        append((word, self.probs[context][word]))

        for key, words in self.sorted_probs.items():
            words.sort(key=lambda x: x[1])
            words.sort(key=lambda x: x[0])

    def generate_sent(self):
        """Randomly generate a sentence."""
        # Construct the ngram context for the first word
        prev_tokens = (self.ngram_model.n-1)*NGram.begin
        sent = []

        word = self.generate_token(tuple(prev_tokens))
        while word != NGram.end[0]:
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

        # Select a position.
        u = random()
        prob_acum = 0.0
        # Determine the interval to which u belongs.
        for word, prob in self.sorted_probs[prev_tokens]:
            prob_acum += prob
            if u <= prob_acum:
                generated_token = word
                break

        assert(generated_token is not None)

        return generated_token


class AddOneNGram(NGram):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        super(AddOneNGram, self).__init__(n, sents)

        self.words = set()

        # Count the words in the vocabulary.
        for sent in sents:
            sent_extended = NGram.begin*(n-1) + sent + NGram.end
            for i in range(len(sent_extended)):
                self.words.add(sent_extended[i])

        self.lenWords = len(self.words)

        # Subtract 1 to self.lenWords, for the beginning symbol.
        if self.n > 1:
            self.lenWords -= 1

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

        assert prev_tokens is not None or self.n == 1

        if prev_tokens is None:
            # {n == 1}
            ret = float(self.count((token,)) + 1) / (self.count(()) +
                                                     self.lenWords)
        else:
            # {prev_tokens is not None}
            tokens = list(prev_tokens)
            tokens.append(token)

            ret = float(self.count(tuple(tokens)) + 1) / \
                (self.count(tuple(prev_tokens)) + self.lenWords)

        return ret

    def V(self):
        """ Size of the vocabulary.
        """
        return self.lenWords


class InterpolatedNGram(NGram):

    def __init__(self, n, sents, gamma=None, addone=True):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        gamma -- interpolation hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """

        self.n = n
        self.words = set()
        self.lenWords = 0
        self.addone = addone
        self.counts = defaultdict(int)

        held_out_set_counts = defaultdict(int)

        if not gamma:
            # We'll need to estimate the gamma parameter. We divide the
            # available data into training and a held out set, over which to
            # estimate gamma.
            len_sents = len(sents)
            len_training_set = floor(0.9*len_sents)
            len_held_out_set = ceil(0.1*len_sents)
            training_set = sents[0: len_training_set]
            held_out_set = sents[len_training_set:
                                 len_training_set+len_held_out_set]

        else:
            # {gamma}
            training_set = list(sents)
            held_out_set = []

        for sent in held_out_set:
            sent_extended = NGram.begin*(self.n-1) + sent + NGram.end

            for i in range(len(sent_extended) - self.n + 1):
                ngram = tuple(sent_extended[i: i+self.n])
                held_out_set_counts[ngram] += 1

        for sent in training_set:
            for j in range(1, self.n+1):
                sent_extended = NGram.begin*j + sent + NGram.end
                # Count every jgram in sent_extended.
                for i in range(len(sent_extended) - j + 1):
                    if j == 1:
                        if addone:
                            self.words.add(sent_extended[i])
                        # Count the words in the corpus.
                        self.counts[()] += 1

                    jgram = tuple(sent_extended[i: i + j])
                    self.counts[jgram] += 1
                if j == 1:
                    # Subtract the symbol <s>.
                    self.counts[()] -= 1

        if addone:
            self.lenWords = len(self.words)

        if not gamma:
            self.__estimate_gamma(held_out_set_counts)
        else:
            self.gamma = gamma

    def __estimate_gamma(self, held_out_set_counts):
        """ Hill climbing algorithm to do a local search of a gamma parameter
            that maximizes the log-likelihood function, over the held-out data.
        """
        gamma_min = 1
        gamma_max = 10000
        step = 500
        gamma = randrange(gamma_min, gamma_max)
        self.gamma = gamma
        L = self.__log_likelihood(held_out_set_counts)

        while step > 0.1:
            # Initialization
            if gamma - step > 0:
                self.gamma = gamma - step
                L_left = self.__log_likelihood(held_out_set_counts)
            else:
                L_left = float("-inf")

            self.gamma = gamma + step
            L_right = self.__log_likelihood(held_out_set_counts)

            # INV : {L is the value of L(...) with parameter gamma and
            #        L_left is the value of L(...) with parameter gamma-step
            #        and
            #        L_right is the value of L(...) with parameter gamma+step}
            while L < L_left or L < L_right:
                if L_left > L and L_left >= L_right:
                    if gamma - step > 0:
                        # gamma-step is the best value seen.
                        gamma = gamma - step
                        # We move to the left.
                        L_right = L
                        L = L_left
                        if gamma - step > 0:
                            self.gamma = gamma - step
                            L_left = self.__log_likelihood(held_out_set_counts)
                        else:
                            break
                    else:
                        # {gamma - step <= 0}
                        self.gamma = gamma
                        break

                elif L_right > L and L_right >= L_left:
                    gamma = gamma + step
                    L_left = L
                    L = L_right
                    self.gamma = gamma + step
                    L_right = self.__log_likelihood(held_out_set_counts)

            step /= 2.0

        self.gamma = gamma

    def __log_likelihood(self, held_out_set_counts):
        """ Evaluates the log-likelihood function over the sentences given.

            held_out_set_counts : a dictionary with the counts of every
            (self.n)-gram seen in the held-out set use for estimation.
        """
        L = 0

        for key, c in held_out_set_counts.items():
            if self.n == 1:
                prev_tokens = None
            else:
                prev_tokens = list(key[:-1])

            prob = self.cond_prob(key[self.n-1], prev_tokens)
            if prob != 0.0:
                L += c*log2(prob)

        return L

    def __calculate_lambda(self, i, prev_tokens, lambdas_prev):
        """ Calculate the lambda_i parameter, as defined in the notes of
            Michael Collins, for the course of NLP, in Columbia University.

            i : number of lambda (1 <= i <= self.n)
            lambdas_prev : list with the values of the previous lambdas.
        """

        sum_lambdas = sum(lambda_j for lambda_j in lambdas_prev)

        ret = (1.0 - sum_lambdas)
        if self.n - i > 0:
            count = self.count(tuple(prev_tokens))
            ret *= float(count)/(count + self.gamma)

        return ret

    def __ngram_cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

        if prev_tokens is None:
            # {self.n == 1}
            if self.addone:
                ret = float(self.count((token,)) + 1) / (self.count(()) +
                                                         self.lenWords)
            else:
                # {not self.addone}
                ret = float(self.count((token,))) / self.count(())
        else:
            # {prev_tokens is not None}
            tokens = list(prev_tokens)
            tokens.append(token)

            count_prev_tokens = self.count(tuple(prev_tokens))
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
        if prev_tokens is None:
            arg_prev_tokens = []
        else:
            # {prev_tokens is not None}
            arg_prev_tokens = list(prev_tokens)

        for i in range(1, self.n+1):
            lambda_i = self.__calculate_lambda(i, arg_prev_tokens, lambdas)
            if lambda_i != 0.0:
                if i < self.n:
                    prob = self.__ngram_cond_prob(token, arg_prev_tokens)
                else:
                    prob = self.__ngram_cond_prob(token)

                ret += lambda_i*prob

            lambdas.append(lambda_i)
            arg_prev_tokens = arg_prev_tokens[1:]

        return ret


class BackOffNGram(NGram):

    def __init__(self, n, sents, beta=None, addone=True):
        """ Back-off NGram model with discounting as described by Michael
            Collins.

        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        beta -- discounting hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """

        self.n = n
        self.words = set()
        self.lenWords = 0
        self.addone = addone
        self.counts = defaultdict(int)
        self.dict_a = {}
        self.denominators = {}
        self.alphas = {}

        if beta is None:
            len_sents = len(sents)
            len_training_set = floor(0.9*len_sents)
            len_held_out_set = ceil(0.1*len_sents)
            training_set = sents[0:len_training_set]
            held_out_set = sents[len_training_set:len_training_set +
                                 len_held_out_set]
        else:
            # {beta is not None}
            training_set = sents
            held_out_set = []
            self.beta = beta

        for sent in training_set:
            sent_completed = NGram.begin*(self.n-1) + sent + NGram.end

            for j in range(1, self.n+1):
                for i in range(len(sent_completed) - j + 1):
                    # Count every j-gram.
                    if j == 1:
                        self.words.add(sent_completed[i])
                        # Count the context of each unigram.
                        self.counts[()] += 1

                    ngram = tuple(sent_completed[i: i+j])
                    self.counts[ngram] += 1

                    # Extend A.
                    top_token = ngram[j-1]
                    context = tuple(ngram[:-1])
                    if len(context) >= 1:
                        if context not in self.dict_a:
                            self.dict_a[context] = {top_token}
                        else:
                            # {context in self.dict_a}
                            self.dict_a[context].add(top_token)
                    # Register in the cache of alphas.
                    self.alphas[context] = 0.0
                if j == 1:
                    self.counts[()] -= self.n-1
        self.lenWords = len(self.words)

        if beta is None:
            if held_out_set != []:
                self.__estimate_beta(held_out_set)
        else:
            self.__calculate_alphas()

        # Calculate denom.
        for ngram in self.dict_a:
            self.denominators[ngram] = self.__calculate_denom(ngram)

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        ret = 0.0
        if prev_tokens is None:
            if self.addone:
                ret = (self.count((token,)) + 1.0) / (self.count(()) +
                                                      self.lenWords)
            else:
                # {not self.addone}
                ret = self.count((token,)) / self.count(())
        else:
            # {prev_tokens is not None}
            prev_tokens_tuple = tuple(prev_tokens)

            if prev_tokens_tuple in self.dict_a and \
                    token in self.dict_a[prev_tokens_tuple]:
                tokens = list(prev_tokens)
                tokens.append(token)

                assert(self.count(prev_tokens_tuple) != 0)

                # MLE approximation of the probability P(token | prev_tokens),
                # with discounting
                ret = (self.count(tuple(tokens)) - self.beta) / \
                    float(self.count(prev_tokens_tuple))

            else:
                # {not prev_tokens_tuple in self.dict_a or not token in \
                #  self.dict_a[tuple(prev_tokens)]}
                den = self.denom(prev_tokens_tuple)

                if den != 0.0:
                    if len(prev_tokens_tuple) > 1:
                        arg_prev_tokens = list(prev_tokens_tuple[1:])
                    else:
                        arg_prev_tokens = None

                    ret = self.alpha(prev_tokens_tuple) * \
                        (self.cond_prob(token, arg_prev_tokens)/den)

        return ret

    def A(self, tokens):
        """Set of words with counts > 0 for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """

        return self.dict_a[tokens]

    def __calculate_alphas(self):
        for key in self.alphas:
            self.alphas[key] = self.__calculate_alpha(key)

    def __calculate_alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        alpha = 1.0
        if tokens in self.dict_a:
            for token in self.dict_a[tokens]:
                # Because "token in self.dict_a[tokens]" holds,
                # self.cond_prob(token, list(tokens)) == Count*(...)/Count(...)

                prob = self.cond_prob(token, list(tokens))
                alpha -= prob
        else:
            self.dict_a[tokens] = set()

        return alpha

    def alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        ret = 1.0
        if tokens in self.alphas:
            ret = self.alphas[tokens]

        return ret

    def __calculate_denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        denom = 1.0
        if len(tokens) == 1:
            prev_tokens = None
        else:
            # {len(tokens} != 1}
            prev_tokens = list(tokens[1:])

        if tokens in self.dict_a:
            for token in self.dict_a[tokens]:
                prob = self.cond_prob(token, prev_tokens)
                denom -= prob
        return denom

    def __calculate_denoms(self):
        for key in self.denominators:
            self.denominators[key] = self.__calculate_denom(key)

    def __estimate_beta(self, held_out_set):
        """ Hill climbing algorithm to do a local search of a beta parameter
            that maximizes the perplexity, over the held-out data.
        """
        assert(held_out_set != [])
        beta_min = 0
        beta_max = 0.9
        step = 0.1
        b_beta = uniform(beta_min, beta_max)
        self.beta = b_beta
        self.__calculate_alphas()
        self.__calculate_denoms()

        m = 0
        for sent in held_out_set:
            m += len(sent)
        c_entropy = self.cross_entropy(held_out_set, m)
        p = self.perplexity(c_entropy)
        # Initialization
        if b_beta - step > 0:
            self.beta = b_beta - step
            self.__calculate_alphas()
            c_entropy = self.cross_entropy(held_out_set, m)
            p_left = self.perplexity(c_entropy)
        else:
            p_left = float("inf")

        self.beta = b_beta + step
        self.__calculate_alphas()
        c_entropy = self.cross_entropy(held_out_set, m)
        p_right = self.perplexity(c_entropy)

        if p_left < p and p_left <= p_right:
            b_beta = b_beta - step
        elif p_right < p and p_right <= p_left:
            b_beta = b_beta + step

        # INV : {p is the perplexity, with parameter beta and
        #        p_left is the perplexity, with parameter beta-step and
        #        p_right is the perplexity, with parameter beta+step and
        #        beta is the best value seen, so far}
        while p > p_left or p > p_right:
            if p_left < p and p_left <= p_right:
                if b_beta - step > 0:
                    # beta-step is the best value seen.
                    b_beta = b_beta - step
                    # We move to the left.
                    p_right = p
                    p = p_left
                    self.beta = b_beta - step
                    self.__calculate_alphas()
                    self.__calculate_denoms()
                    c_entropy = self.cross_entropy(held_out_set, m)
                    p_left = self.perplexity(c_entropy)
                else:
                    # {beta - step <= 0}
                    self.beta = b_beta
                    self.__calculate_alphas()
                    self.__calculate_denoms()
                    break

            elif p_right < p and p_right <= p_left:
                b_beta = b_beta + step
                p_left = p
                p = p_right
                self.beta = b_beta + step
                self.__calculate_alphas()
                self.__calculate_denoms()
                c_entropy = self.cross_entropy(held_out_set, m)
                p_right = self.perplexity(c_entropy)

        self.beta = b_beta
        self.__calculate_alphas()
        self.__calculate_denoms()

    def denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """

        if tokens in self.denominators:
            ret = self.denominators[tokens]
        else:
            ret = self.__calculate_denom(tokens)
            self.denominators[tokens] = ret

        return ret
