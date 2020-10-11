#!/usr/bin/env python
# coding: utf-8
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk import sent_tokenize
import numpy as np
import networkx as nx
from pprint import pprint
from stringtodict import ListFromString


def read_messages(file_name):
    list_of_sentences = ListFromString()
    all_sents = [sent_tokenize(sent['content']) for sent in list_of_sentences]
    flat_list = [item for sublist in all_sents for item in sublist]
    final_sentences = []
    for sentence in flat_list:
        if len(sentence)>5:
            final_sentences.append(sentence)
    return final_sentences


def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w not in stopwords:
            vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w not in stopwords:
            vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(
                sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(file_name):
    stop_words = stopwords.words('english')
    summarize_text = []
    sentences = read_messages(file_name)
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)
    ranked_sentence = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    top_n = len(ranked_sentence)//(100//8)
    for i in range(top_n):
        summarize_text.append("".join(ranked_sentence[i][1]))
    return ". ".join(summarize_text)

summarized_string = generate_summary("paragraph.txt")

if __name__ == "__main__":
    print(summarized_string)