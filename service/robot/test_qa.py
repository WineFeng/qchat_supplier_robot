#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
import service.cnn.question_model as qm
from service.cnn.question_handle import question_to_vector, format_question
import tensorflow as tf
from service.robot.model_config import project_dir, result_dir, PRE_PARAM, FLAGS, qa_file_path, qa_file_default, \
    is_segment
import os
from utils.tsvh_file import TsvhFileReader
import re
import jieba
from utils.text_segmentor import TextSegmentor
from get_config import get_logger_file
import traceback

logger = get_logger_file('test')

print("Loading supplier data...")
all_bytpe_graph_sess = {}
all_btype_question_dict = {}
stop_words_file = "./stop_words.txt"


def segment_question(text):
    question = []
    stop_words = [line.strip() for line in
                  open(stop_words_file).readlines()]
    print(list(jieba.cut(text)))
    for word in list(jieba.cut(text)):
        if word not in stop_words:
            question.append(word)
    if question:
        print("question={}".format(question))
        return question
    else:
        print(text)
        return text


def init_btype_graph(btype):
    tf.reset_default_graph()
    bytes_graph = tf.Graph()
    checkpoint_file = qm.get_last_checkpoint_dir(project_dir, result_dir, btype)
    print("check point file {}".format(checkpoint_file))
    vocab_file_path = os.path.join(checkpoint_file.split("/checkpoints/")[0],
                                   eval("FLAGS.{}_vocab_filename".format(PRE_PARAM)))
    print("vocabulary file {}".format(vocab_file_path))
    print("FLAGS.{}_vocab_filename".format(PRE_PARAM))
    vocabulary = {}
    for v in TsvhFileReader(vocab_file_path).open():
        vocabulary[v["vocab"]] = int(v["idx"])
    for v in TsvhFileReader(vocab_file_path).open():
        vocabulary[v["vocab"]] = int(v["idx"])
    with bytes_graph.as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=True,
            log_device_placement=False)
        btype_sess = tf.Session(config=session_conf)
        with btype_sess.as_default():
            # Load the saved meta graph and restore variables
            saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
            saver.restore(btype_sess, checkpoint_file)
    return bytes_graph, btype_sess, vocabulary


def btype_test(question, btype):
    segmentor = TextSegmentor()
    global all_bytpe_graph_sess
    question = format_question(question)
    qtype = ''
    try:
        if all_bytpe_graph_sess.get(btype) is None:
            all_bytpe_graph_sess[btype] = init_btype_graph(btype)
        bytes_graph, btype_sess, vocabulary = all_bytpe_graph_sess.get(btype)
        question_vector = question_to_vector(question, vocabulary,
                                             eval("FLAGS.{}_max_question_length".format(PRE_PARAM)))
        qtype = qm.learn(bytes_graph, btype_sess, question_vector)
    except:
        logger.error("test_qa test_type question={},btype={}".format(question, btype))
        logger.error(traceback.format_exc())
    return qtype


def get_qa_data(btype):
    question_dict = {}
    btype_dict = {}
    try:
        qa_file = qa_file_path.format(btype)
        if not os.path.exists(qa_file):
            qa_file = qa_file_default
        for qa in TsvhFileReader(qa_file).open():
            qtype = int(qa.get("qtype"))
            # qa["answer"] = re.sub(r"\\n", r"\n", qa.get("answer"))
            qa["answer"] = qa.get("answer")
            btype_dict[qtype] = qa
            question_dict[qa.get("question")] = qa
    except:
        logger.error("test_qa get qa_{}.txt failed".format(btype))
        logger.error(traceback.format_exc())

    return btype_dict, question_dict


def get_answer_dict(question, business_id, supplier_id):
    btype = "{}_{}".format(business_id, supplier_id)
    global all_btype_question_dict
    ret_dict = {}
    try:
        if all_btype_question_dict.get(btype) is None:
            btype_dict, question_dict = get_qa_data(btype)
            all_btype_question_dict[btype] = (btype_dict, question_dict)
        btype_dict, question_dict = all_btype_question_dict.get(btype)
        qa_dict = question_dict.get(question, {})
        print("qa_dict={}".format(qa_dict))
        if not len(qa_dict):
            qtype = btype_test(question, btype)
            qa_dict = btype_dict.get(qtype, {})
        ret_dict.update(qa_dict)
        answer = ret_dict.get("answer", "对不起,我还无法理解您的问题,请您点击下方【找人工客服】为您提供服务，感谢您的咨询。")
        ret_dict["answer"] = answer
        logger.info("get_answer_dict ret_dict={}".format(ret_dict))
    except:
        logger.error(
            "test_qa get_answer failed question={}, business_id={}, supplier_id={}".format(question, business_id,
                                                                                           supplier_id))
        logger.error(traceback.format_exc())
    return ret_dict


if __name__ == '__main__':
    # segment_question("")
    get_answer_dict("你好", 0, 0)
