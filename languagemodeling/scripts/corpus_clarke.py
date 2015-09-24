from nltk.tokenize import RegexpTokenizer

""" Data about the corpus.
"""

pattern = r'''(?ix)    # set flag to allow verbose regexps
              (Arthur\sC\.\sClarke)
            | (Heywood\sFloyd)
            | (Frank\sPoole)
            | (David\sBowman)
            | (Richard\sWakefield)
            | (Nicole\sdes\sJardins)
            | (Francesca\sSabatini)
            | (Elaine\sBrown)
            | (David\sBrown)
            | ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
            | \w+(-\w+)*        # words with optional internal hyphens
            | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
            | \.\.\.            # ellipsis
            | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
            '''
corpus_clarke_tokenizer = RegexpTokenizer(pattern)

corpus_clarke_name = "Corpus Clarke"
corpus_clarke_training_name = "Corpus Clarke Entrenamiento"
corpus_clarke_tests_name = "Corpus Clarke Tests"
