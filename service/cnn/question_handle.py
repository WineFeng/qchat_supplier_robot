#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
import numpy as np
import re
import itertools
from collections import Counter
from utils.tsvh_file import TsvhFileReader


UNKOWN_STR = 'unk'
PAD_STR = 'pad'

def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def format_question(question):
    question = re.sub(",|，|。|\.|\?|？|!|！|\s+|\\\\n", "", question)
    question = question.strip("吗|么|/")
    return question


def load_data_and_labels(train_file):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    y = []
    x_text = []
    for question_dict in TsvhFileReader(train_file).open():
        question = question_dict["question"]
        qtype = int(question_dict["type"])
        x_text.append(list(question))
        type_list = [0] * 10
        type_list[qtype] = 1
        y.append(type_list)
    return [x_text, y]


def pad_sentences(sentences, sequence_length=0):
    """
    Pads all sentences to the same length. The length is defined by the longest sentence.
    Returns padded sentences.
    """
    if sequence_length == 0:
        sequence_length = max(len(x) for x in sentences)
    padded_sentences = []
    for i in range(len(sentences)):
        sentence = sentences[i]
        num_padding = sequence_length - len(sentence)
        if num_padding > 0:
            new_sentence = sentence + [PAD_STR] * num_padding
        else:
            new_sentence = sentence[0:sequence_length]
        padded_sentences.append(new_sentence)
    return padded_sentences


def build_vocab(sentences):
    """
    Builds a vocabulary mapping from word to index based on the sentences.
    Returns vocabulary mapping and inverse vocabulary mapping.
    """
    # Build vocabulary
    word_counts = Counter(itertools.chain(*sentences))
    word_counts[UNKOWN_STR] = 999999
    word_counts[PAD_STR] = 999999
    # Mapping from index to word
    vocabulary_inv = [x[0] for x in word_counts.most_common()]
    # Mapping from word to index
    vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
    return [vocabulary, vocabulary_inv]


def build_input_data(sentences, labels, vocabulary):
    """
    Maps sentencs and labels to vectors based on a vocabulary.
    """
    x = np.array([[vocabulary[word] for word in sentence] for sentence in sentences])
    y = np.array(labels)
    return [x, y]


def load_data(train_file, max_question_length=0):
    """
    Loads and preprocessed data for dataset.
    Returns input vectors, labels, vocabulary, and inverse vocabulary.
    """
    # Load and preprocess data
    sentences, labels = load_data_and_labels(train_file)
    sentences_padded = pad_sentences(sentences, sequence_length=max_question_length)
    vocabulary, vocabulary_inv = build_vocab(sentences_padded)
    x, y = build_input_data(sentences_padded, labels, vocabulary)
    return [x, y, vocabulary, vocabulary_inv]


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    print('before np.array is :\n {}'.format(data))
    data = np.array(data)
    print('data after np.array is :\n {}'.format(data))
    data_size = len(data)
    print(data_size)
    num_batches_per_epoch = int(len(data) / batch_size) + 1
    print(num_batches_per_epoch)
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        # print("the train epoch={}".format(epoch))
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            print('start_index is : {}'.format(start_index))
            print('end_index is : {}'.format(end_index))
            # maybe the start_index is equal end_index, the length data is 0
            if start_index == end_index:
                start_index = start_index - batch_size
            yield shuffled_data[start_index:end_index]


def question_to_vector(question_string, vocabulary, sequence_length=0):
    """
    string quetion to the vecotor data for train or learn
    """
    new_question = question_string.strip().lower()
    new_question = new_question.split(' ') if ' ' in new_question else list(new_question)
    num_padding = sequence_length - len(new_question)
    if num_padding > 0:
        new_sentence = new_question + [PAD_STR] * num_padding
    else:
        new_sentence = new_question[0: sequence_length]
    print('look here :\n {}'.format([vocabulary.get(word, vocabulary.get(UNKOWN_STR)) for word in new_sentence]))
    print('look here :\n {}'.format(np.array([vocabulary.get(word, vocabulary.get(UNKOWN_STR)) for word in new_sentence])))
    x = np.array([vocabulary.get(word, vocabulary.get(UNKOWN_STR)) for word in new_sentence])
    question_vector = np.array([x])
    print('return questionvector : {}'.format(question_vector))
    return question_vector



