#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys

sys.path.append("././")
from utils.tsvh_file import TsvhFileReader
from service.robot.model_config import qa_file_path, FLAGS, PRE_PARAM, project_dir, result_dir
from service.cnn.question_handle import pad_sentences, build_input_data, build_vocab
import service.cnn.question_model as qm
from get_config import get_logger_file
from db.get_database_data import SupplierQaData
from service.robot.qa_data import write_qa_data
import traceback

logger = get_logger_file('train')


def paser_qa_data(btype):
    myapps_ad = {}
    x_text = []
    y_text = []
    qa_list = []
    max_qtype = 0
    try:
        for qa in TsvhFileReader(qa_file_path.format(btype)).open():
            qa_list.append(qa)
            if qa.get("qtype") == '':
                qa["qtype"] = 0
            else:
                qa["qtype"] = int(qa.get("qtype"))
            qa["qtype"] = qa.get("qtype", "0")
            if qa.get("qtype") > max_qtype:
                max_qtype = qa.get("qtype")
        max_qtype += 1
        FLAGS.__setattr__("{}_num_classes".format(PRE_PARAM), max_qtype)
        logger.info("train_qa get_qa_list={}".format(qa_list))
        for qa in qa_list:
            question = qa.get("question")
            qtype = qa.get("qtype")
            myapps_ad[qtype] = qa.get("answer")
            n_len = len(question)
            for i in range(min(4, n_len), n_len + 1):
                for j in range(0, n_len - i + 1):
                    x_text.append(list(question[j: j + i]))
                    type_list = [0] * max_qtype
                    type_list[qtype] = 1
                    y_text.append(type_list)
    except:
        logger.error("train_qa get qa_{}.txt failed".format(btype))
        logger.error(traceback.format_exc())
    return [x_text, y_text, myapps_ad]


def qa_train(business_id=0, supplier_id=0):
    logger.info("Loading data...")
    btype = "{}_{}".format(business_id, supplier_id)

    sentences, labels, myapps_answer_dict = paser_qa_data(btype)
    sentences_padded = pad_sentences(sentences, sequence_length=eval("FLAGS.{}_max_question_length".format(PRE_PARAM)))
    vocabulary, vocabulary_inv = build_vocab(sentences_padded)
    x, y = build_input_data(sentences_padded, labels, vocabulary)
    qm.train(x, y, vocabulary, FLAGS, project_dir, result_dir, PRE_PARAM, btype)
    # return myapps_answer_dict


if __name__ == '__main__':
    qa_train(business_id=0, supplier_id=0)
    bs_list = SupplierQaData.select_btype()
    if bs_list:
        for business_id, supplier_id in bs_list:
            write_qa_data(business_id=business_id, supplier_id=supplier_id)
            qa_train(business_id=business_id, supplier_id=supplier_id)
