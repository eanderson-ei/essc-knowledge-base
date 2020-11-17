"""Text rank extracts keywords
https://towardsdatascience.com/textrank-for-keyword-extraction-by-python-\
    c0bae21bcec0
Modified to rank named entities instead of words, updated for english
and spanish
"""

import spacy
from spacy.pipeline import EntityRuler
from collections import OrderedDict
import numpy as np
from spacy.lang.en.stop_words import STOP_WORDS as STOP_WORDS_EN
from spacy.lang.es.stop_words import STOP_WORDS as STOP_WORDS_ES

STOP_WORDS = STOP_WORDS_EN | STOP_WORDS_ES

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp, overwrite_ents=True).from_disk('data/inputs/entity-patterns.jsonl')
nlp.add_pipe(ruler, before="ner")

class TextRank4Keyword():
    """Extract keywords from text"""
    
    def __init__(self):
        self.d = 0.65 # damping coefficient, usually is .85
        self.min_diff = 1e-5 # convergence threshold
        self.steps = 10 # iteration steps
        self.node_weight = None # save keywords and its weight

    
    def set_stopwords(self, stopwords):  
        """Set stop words"""
        for word in STOP_WORDS.union(set(stopwords)):
            lexeme = nlp.vocab[word]
            lexeme.is_stop = True
    
    def sentence_segment(self, doc, not_entity_types, lower=False):
        """Store those words only in cadidate_pos"""
        sentences = []
        for sent in doc.sents:
            selected_words = []
            for entity in sent.ents:  # entities instead of words
                # Store words only with cadidate POS tag
                if entity.label_ not in not_entity_types \
                    and entity.text not in STOP_WORDS:
                    # use entity id if present
                    if entity.ent_id_:  # isinstance(entity.ent_id, str):
                        tag = entity.ent_id_
                    else:
                        tag = entity.text
                    if lower is True:
                        selected_words.append(tag.lower())
                    else:
                        selected_words.append(tag)
                    if entity.label_=="ALT":
                        pass
            sentences.append(selected_words)
        return sentences
        
    def get_vocab(self, sentences):
        """Get all tokens"""
        vocab = OrderedDict()
        i = 0
        for sentence in sentences:
            for word in sentence:
                if word not in vocab:
                    vocab[word] = i
                    i += 1
        return vocab
    
    def get_token_pairs(self, window_size, sentences):
        """Build token_pairs from windows in sentences"""
        token_pairs = list()
        for sentence in sentences:
            for i, word in enumerate(sentence):
                for j in range(i+1, i+window_size):
                    if j >= len(sentence):
                        break
                    pair = (word, sentence[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs
        
    def symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())
    
    def get_matrix(self, vocab, token_pairs):
        """Get normalized matrix"""
        # Build matrix
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')
        for word1, word2 in token_pairs:
            i, j = vocab[word1], vocab[word2]
            g[i][j] = 1
            
        # Get Symmetric matrix
        g = self.symmetrize(g)
        
        # Normalize matrix by column
        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm!=0) # this is ignore the 0 element in norm
        
        return g_norm

    
    def get_keywords(self, number=10):
        """Print top number keywords"""
        keywords = {}
        node_weight = OrderedDict(sorted(self.node_weight.items(), 
                                         key=lambda t: t[1], reverse=True))
        keywords = {k: node_weight[k] for k in list(node_weight)[:number]}
        return keywords
        # for i, (key, value) in enumerate(node_weight.items()):
        #     # keywords.append(f'{i+1}) {key} - {str(value)}')
        
        
    def analyze(self, text, 
                not_entity_types=['DATE', 'TIME', 'PERCENT',
                                   'MONEY', 'QUANTITY', 'ORDINAL',
                                   'CARDINAL', 'PERSON', 'GPE'], 
                window_size=4, lower=False, stopwords=set(STOP_WORDS)):
        """Main function to analyze text"""
        
        # Set stop words
        self.set_stopwords(stopwords)
        
        # Pare text by spaCy
        doc = nlp(text)
        
        # Filter sentences
        sentences = self.sentence_segment(doc, not_entity_types, lower) # list of list of words
        
        # Build vocabulary
        vocab = self.get_vocab(sentences)
        
        # Get token_pairs from windows
        token_pairs = self.get_token_pairs(window_size, sentences)
        
        # Get normalized matrix
        g = self.get_matrix(vocab, token_pairs)
        
        # Initialization for weight(pagerank value)
        pr = np.array([1] * len(vocab))
        
        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr = (1-self.d) + self.d * np.dot(g, pr)
            if abs(previous_pr - sum(pr))  < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weight = dict()
        for word, index in vocab.items():
            node_weight[word] = pr[index]
        
        self.node_weight = node_weight

if __name__=='__main__':
    

    with open('data/processed/text2.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        
    doc = nlp(text)

    # # drop stop words  # not needed b/c using entities
    # candidate_pos = ['NOUN', 'PROPN', 'VERB']
    # sentences = []

    # for sent in doc.sents:
    #     selected_words=[]
    #     for token in sent:
    #         if token.pos_ in candidate_pos and token.is_stop is False:
    #             selected_words.append(token)
    #     sentences.append(selected_words)

    tr4w = TextRank4Keyword()
    tr4w.analyze(text, window_size=4, lower=False)
    tr4w.get_keywords(20)