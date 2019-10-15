#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys

sys.path.append("././")
import tensorflow as tf
import os
import re

# Parameters
# ==================================================

PRE_PARAM = 'robot'

# Model Hyperparameters
tf.flags.DEFINE_integer("{}_embedding_dim".format(PRE_PARAM), 128,
                        "Dimensionality of character embedding (default: 128)")
tf.flags.DEFINE_string("{}_filter_sizes".format(PRE_PARAM), "3,4,5", "Comma-separated filter sizes (default: '3,4,5')")
tf.flags.DEFINE_integer("{}_num_filters".format(PRE_PARAM), 128, "Number of filters per filter size (default: 128)")
tf.flags.DEFINE_float("{}_dropout_keep_prob".format(PRE_PARAM), 0.5, "Dropout keep probability (default: 0.5)")
tf.flags.DEFINE_float("{}_l2_reg_lambda".format(PRE_PARAM), 0.0, "L2 regularizaion lambda (default: 0.0)")
#
# Training parameters
tf.flags.DEFINE_integer("{}_batch_size".format(PRE_PARAM), 256, "Batch Size (default: 64)")
tf.flags.DEFINE_integer("{}_num_epochs".format(PRE_PARAM), 10, "Number of training epochs (default: 200)")
tf.flags.DEFINE_integer("{}_evaluate_every".format(PRE_PARAM), 100,
                        "Evaluate model on dev set after this many steps (default: 100)")
tf.flags.DEFINE_integer("{}_checkpoint_every".format(PRE_PARAM), 100, "Save model after this many steps (default: 100)")
# Misc Parameters
tf.flags.DEFINE_boolean("{}_allow_soft_placement".format(PRE_PARAM), True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("{}_log_device_placement".format(PRE_PARAM), False, "Log placement of ops on devices")

# Model config
tf.flags.DEFINE_integer("{}_num_classes".format(PRE_PARAM), 0, "the size of classes")
tf.flags.DEFINE_integer("{}_max_question_length".format(PRE_PARAM), 60, "the max lenght of question")
tf.flags.DEFINE_string("{}_model_name".format(PRE_PARAM), "qestion_model.ckpt", "the model name")
tf.flags.DEFINE_integer("{}_test_num".format(PRE_PARAM), 1, "the num of test set from all the answer data")
tf.flags.DEFINE_string("{}_vocab_filename".format(PRE_PARAM), "vocabulary.data", "the vocabulary data file name")

FLAGS = tf.flags.FLAGS
# FLAGS.flag_values_dict()

print("\nParameters:")
for attr, value in sorted(FLAGS.flag_values_dict().items()):
    print("{}={}".format(attr.upper(), value))
print("")

project_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[1]
result_dir = "model"
data_dir = "data"
qa_filename = "qa_{}.txt"
is_segment = True
if is_segment:
    qa_file_path = 'qa_{}.txt'
qa_file_path = os.path.join(project_dir, data_dir, qa_filename)
qa_file_default = os.path.join(project_dir, data_dir, "qa_0_0.txt")

business_id_map = {}
