import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")

stemmer = RSLPStemmer()

def tokenize(sentence):
    return word_tokenize(sentence, language='portuguese')

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, words):
    sentence_word = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)

    for idx, w in enumerate(words):
        if w in sentence_word:
            bag[idx] = 1.0
    return bag