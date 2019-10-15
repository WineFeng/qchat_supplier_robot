#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tensorflow as tf
from tensorflow.python.ops import rnn_cell


class QuestionCNN(object):
    """
    A CNN for question classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    def __init__(
            self, sequence_length, num_classes, vocab_size,
            embedding_size, filter_sizes, num_filters, l2_reg_lambda=0.0):
        self.sequence_length = sequence_length
        # Placeholders for input, output and dropout
        self.input_x = tf.placeholder(tf.int32, [None, sequence_length],
                                      name="input_x")  # sequence_length个列， 一般是sequence_length = 60列
        self.input_y = tf.placeholder(tf.float32, [None, num_classes], name="input_y")  # num_classes可能是每一列的数量，不确定
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        # Keeping track of l2 regularization loss (optional)
        l2_loss = tf.constant(0.0)
        # self.rnn_sequence_length = tf.cast(self.sequence_length, tf.int32)
        lstm_cell = rnn_cell.BasicLSTMCell(num_filters, forget_bias=1.0)
        r_cell = rnn_cell.BasicRNNCell(num_filters)  # num_filters =RNN层神经元个数
        # Get lstm cell output
        self.cell = rnn_cell.MultiRNNCell([lstm_cell, r_cell], state_is_tuple=True)

        # Embedding layer
        with tf.device('/cpu:0'), tf.name_scope("embedding"):
            W_E = tf.Variable(
                tf.random_uniform([vocab_size, embedding_size], -1.0, 1.0),
                name="W_E")
            self.embedded_chars = tf.nn.embedding_lookup(W_E, self.input_x)
            self.embedded_chars_expanded = tf.expand_dims(self.embedded_chars, -1)

        cnn_input = self.embedded_chars_expanded

        # Create a convolution + maxpool layer for each filter size
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-%s" % filter_size):
                h = self.CNN(cnn_input, filter_size, embedding_size, num_filters)
                # Maxpooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, sequence_length - filter_size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)

        # Combine all the pooled features
        num_filters_total = num_filters * len(filter_sizes)
        self.h_pool = tf.concat(pooled_outputs, 3)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])

        # Add dropout
        with tf.name_scope("dropout"):
            self.h_drop = tf.nn.dropout(self.h_pool_flat, self.dropout_keep_prob)

        # Final (unnormalized) scores and predictions
        with tf.name_scope("output"):
            W = tf.get_variable(
                "W_output",
                shape=[num_filters_total, num_classes],
                initializer=tf.contrib.layers.xavier_initializer())
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b_output")
            l2_loss += tf.nn.l2_loss(W)
            l2_loss += tf.nn.l2_loss(b)
            self.scores = tf.nn.xw_plus_b(self.h_drop, W, b, name="scores")
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        # CalculateMean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.softmax_cross_entropy_with_logits(logits=self.scores, labels=self.input_y)
            self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")

    def CNN(self, cnn_input, filter_size, embedding_size, num_filters):
        # Convolution Layer
        filter_shape = [filter_size, embedding_size, 1, num_filters]
        W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name="W_{}".format(filter_size))
        b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b_{}".format(filter_size))
        conv = tf.nn.conv2d(
            cnn_input,
            W,
            strides=[1, 1, 1, 1],
            padding="VALID",
            name="conv")
        # Apply nonlinearity
        h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
        return h
