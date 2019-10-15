#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
import tensorflow as tf
import numpy as np
import os
import time
import datetime
from service.cnn import question_handle
from service.cnn.question_cnn import QuestionCNN
from utils.tsvh_file import TsvhFileWriter


def train(x, y, vocabulary, FLAGS, project_dir, result_dir, pre_param, btype=None):
    # Randomly shuffle data
    np.random.seed(10)
    shuffle_indices = np.random.permutation(np.arange(len(y)))
    x_shuffled = x[shuffle_indices]
    y_shuffled = y[shuffle_indices]
    # Split train/test set
    # TODO: This is very crude, should use cross-validation
    test_num = FLAGS.__getattr__("{}_test_num".format(pre_param))
    # x_train, x_dev = x_shuffled[:-test_num], x_shuffled[-test_num:]
    # y_train, y_dev = y_shuffled[:-test_num], y_shuffled[-test_num:]
    x_train, x_dev = x_shuffled, x_shuffled[-test_num:]
    y_train, y_dev = y_shuffled, y_shuffled[-test_num:]
    print("Vocabulary Size: {:d}".format(len(vocabulary)))
    print("Train/Dev split: {:d}/{:d}".format(len(y_train), len(y_dev)))

    # Training
    # ==================================================

    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=FLAGS.__getattr__("{}_allow_soft_placement".format(pre_param)),
            log_device_placement=FLAGS.__getattr__("{}_log_device_placement".format(pre_param)))
        sess = tf.Session(config=session_conf)
        # sess = tf.Session()
        with sess.as_default():
            cnn = QuestionCNN(
                sequence_length=x_train.shape[1],
                num_classes=FLAGS.__getattr__("{}_num_classes".format(pre_param)),
                vocab_size=len(vocabulary),
                embedding_size=FLAGS.__getattr__("{}_embedding_dim".format(pre_param)),
                filter_sizes=list(map(int, FLAGS.__getattr__("{}_filter_sizes".format(pre_param)).split(","))),
                num_filters=FLAGS.__getattr__("{}_num_filters".format(pre_param)),
                l2_reg_lambda=FLAGS.__getattr__("{}_l2_reg_lambda".format(pre_param)))

            # Define Training procedure
            global_step = tf.Variable(0, name="global_step", trainable=False)
            optimizer = tf.train.AdamOptimizer(1e-3)
            grads_and_vars = optimizer.compute_gradients(cnn.loss)
            train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)

            # Keep track of gradient values and sparsity (optional)
            grad_summaries = []
            for g, v in grads_and_vars:
                if g is not None:
                    name = v.name.split(":")[0]
                    grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(name), g)
                    sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(name), tf.nn.zero_fraction(g))
                    grad_summaries.append(grad_hist_summary)
                    grad_summaries.append(sparsity_summary)
            grad_summaries_merged = tf.summary.merge(grad_summaries)

            # Output directory for models and summaries
            timestamp = str(int(time.time()))
            dir_name = timestamp
            if btype:
                dir_name = "{}_{}".format(timestamp, btype)
            out_dir = os.path.abspath(os.path.join(project_dir, result_dir, dir_name))
            print("Writing to {}\n".format(out_dir))

            # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
            checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))

            checkpoint_prefix = os.path.join(checkpoint_dir, FLAGS.__getattr__("{}_model_name".format(pre_param)))

            # Use the relative path has no path mode name in checkpoint
            # checkpoint_prefix = checkpoint_prefix.replace(project_dir, ".")

            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)

            vocab_w = TsvhFileWriter(os.path.join(out_dir, FLAGS.__getattr__("{}_vocab_filename".format(pre_param))),
                                     keys="vocab,idx")
            for v_word, v_idx in list(vocabulary.items()):
                vocab_w.write({"vocab": v_word, "idx": v_idx})
            vocab_w.close()
            saver = tf.train.Saver(tf.global_variables())

            # Summaries for loss and accuracy
            loss_summary = tf.summary.scalar("loss", cnn.loss)
            acc_summary = tf.summary.scalar("accuracy", cnn.accuracy)

            # Train Summaries
            train_summary_op = tf.summary.merge([loss_summary, acc_summary, grad_summaries_merged])
            train_summary_dir = os.path.join(out_dir, "summaries", "train")
            train_summary_writer = tf.summary.FileWriter(train_summary_dir, sess.graph)

            # Dev summaries
            dev_summary_op = tf.summary.merge([loss_summary, acc_summary])
            dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
            dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, sess.graph)

            # Initialize all variables
            sess.run(tf.global_variables_initializer())

            def train_step(x_batch, y_batch):
                """
                A single training step
                """
                feed_dict = {
                    cnn.input_x: x_batch,
                    cnn.input_y: y_batch,
                    cnn.dropout_keep_prob: FLAGS.__getattr__("{}_dropout_keep_prob".format(pre_param))
                }
                _, step, summaries, loss, accuracy = sess.run(
                    [train_op, global_step, train_summary_op, cnn.loss, cnn.accuracy],
                    feed_dict)
                time_str = datetime.datetime.now().isoformat()
                print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
                train_summary_writer.add_summary(summaries, step)

            def dev_step(x_batch, y_batch, writer=None):
                """
                Evaluates model on a dev set
                """
                feed_dict = {
                    cnn.input_x: x_batch,
                    cnn.input_y: y_batch,
                    cnn.dropout_keep_prob: 1.0
                }
                step, summaries, loss, accuracy = sess.run(
                    [global_step, dev_summary_op, cnn.loss, cnn.accuracy],
                    feed_dict)
                time_str = datetime.datetime.now().isoformat()
                print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
                if writer:
                    writer.add_summary(summaries, step)

            # Generate batches
            batch_size = FLAGS.__getattr__("{}_batch_size".format(pre_param))
            num_epochs = FLAGS.__getattr__("{}_num_epochs".format(pre_param))
            evaluate_every = FLAGS.__getattr__("{}_evaluate_every".format(pre_param))
            checkpoint_every = FLAGS.__getattr__("{}_checkpoint_every".format(pre_param))
            batches = question_handle.batch_iter(
                list(zip(x_train, y_train)), batch_size, num_epochs)
            # Training loop. For each batch...
            for batch in batches:
                if len(batch) == 0:
                    continue
                x_batch, y_batch = list(zip(*batch))
                train_step(x_batch, y_batch)
                current_step = tf.train.global_step(sess, global_step)
                if current_step % evaluate_every == 0:
                    print("\nEvaluation:")
                    dev_step(x_dev, y_dev, writer=dev_summary_writer)
                    print("")
                if current_step % checkpoint_every == 0:
                    path = saver.save(sess, checkpoint_prefix, global_step=current_step)
                    print("Saved model checkpoint to {}\n".format(path))
            print("\nEvaluation:")
            dev_step(x_dev, y_dev, writer=dev_summary_writer)
            print("")
            path = saver.save(sess, checkpoint_prefix, global_step=current_step)
            print("Saved model checkpoint to {}\n".format(path))


def learn(graph, sess, question_vector):
    # Get the placeholders from the graph by name
    input_x = graph.get_operation_by_name("input_x").outputs[0]
    # input_y = graph.get_operation_by_name("input_y").outputs[0]
    dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

    # Tensors we want to evaluate
    predictions = graph.get_operation_by_name("output/predictions").outputs[0]

    # Generate batches for one epoch
    batches = question_handle.batch_iter(question_vector, 30, 1, shuffle=False)

    # Collect the predictions here
    # all_predictions = []

    for x_test_batch in batches:
        print('batche is {}'.format(x_test_batch))
        batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
        print('batch_predictions is {}'.format(batch_predictions))
        # print batch_predictions
        # all_predictions = np.concatenate([all_predictions, batch_predictions])
        # print all_predictions
    tf.reset_default_graph()
    return int(batch_predictions[0])


def get_last_checkpoint_dir(project_dir, result_dir, btype=None):
    runs_dir = os.path.join(project_dir, result_dir)
    all_run_dir = os.listdir(runs_dir)
    all_run_dir = list(filter(lambda x: os.path.isdir(os.path.join(project_dir, runs_dir, x)), all_run_dir))
    last_time = sorted(all_run_dir, reverse=True)[0]

    if btype:
        time_files = []
        for name in all_run_dir:
            if name.endswith(btype):
                time_files.append(name.split("_")[0])
        if time_files:
            last_time = sorted(time_files, reverse=True)[0]
            last_time = "{}_{}".format(last_time, btype)
    checkpoint_dir = "{}/{}/checkpoints".format(runs_dir, last_time)
    checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)
    return checkpoint_file
