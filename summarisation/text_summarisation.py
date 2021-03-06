import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.corpus import words
import numpy as np
import networkx as nx
from collections import Counter
import re

def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)

def create_common_word_list(list_of_sentences):
    file = open('summarisation/very_common_words.txt', 'r')
    file_string = file.read()
    common_word_list = file_string.split('\n')
    all_names = [sent['author'] for sent in list_of_sentences]
    all_names = list(set(all_names))
    common_word_list.append(all_names)
    return common_word_list


def read_messages(list_of_sentences):
    all_sents = [sent_tokenize(sent['content']) for sent in list_of_sentences]
    flat_list = [item for sublist in all_sents for item in sublist]
    pre_final_sentences = []
    for sentence in flat_list:
        if len(sentence) > 5:
            pre_final_sentences.append(sentence)
    final_sentences = []
    sentence_enders = ['.', '!', '?']
    for sentence in pre_final_sentences:
        sentence = re.sub(r'@[a-zA-Z]*\s', '', sentence)
        sentence = re.sub('> ','',sentence)
        sentence = deEmojify(sentence)
        if sentence[-1] not in sentence_enders:
            sentence = sentence+'.'
        final_sentences.append(sentence)
    return final_sentences


def sentence_similarity(sent1, sent2, common_word_list, stopwords=None):

    if stopwords is None:
        stopwords = []
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w not in stopwords and w not in common_word_list:
            vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w not in stopwords and w not in common_word_list:
            vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words, common_word_list):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(
                sentences[idx1], sentences[idx2], stop_words, common_word_list)

    return similarity_matrix

def generate_summary(messages, percentage=8):
    stop_words = stopwords.words('english')
    summarize_text = []
    common_word_list = create_common_word_list(messages)
    sentences = read_messages(messages)
    sentence_similarity_martix = build_similarity_matrix(
        sentences, stop_words, common_word_list)
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)
    ranked_sentence = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    top_n = len(ranked_sentence)//(100//percentage)
    for i in range(top_n):
        summarize_text.append("".join(ranked_sentence[i][1]))
    return " ".join(summarize_text)

def generate_keywords(messages, n=8):
    sentences = read_messages(messages)
    stop_words = stopwords.words('english')
    words = []
    common_word_list = create_common_word_list(messages)
    for sentence in sentences:
        sentence_words = word_tokenize(sentence)
        for i in range(len(sentence_words)):
            sentence_words[i] = sentence_words[i].lower()
        words.append(sentence_words)
    flat_words = [item for sublist in words for item in sublist]
    final_wordlist = []
    for flat_word in flat_words:
        if flat_word not in stop_words and len(flat_word) > 3:
            final_wordlist.append(flat_word)
    freq = Counter(final_wordlist)
    common_keywords = (freq.most_common(n))
    final_words = []
    for c in common_keywords:
        if c[0] not in common_word_list:
            final_words.append(c[0])
    return final_words
