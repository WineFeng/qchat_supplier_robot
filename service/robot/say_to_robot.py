#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys

sys.path.append("././")
from service.robot.test_qa import get_answer_dict, get_qa_data
from utils.question_format_util import QuestionFormatUtil
from db.get_database_data import SupplierRobotConfig, SupplierQaHistory
import json
from utils.send_message_util import SendMessageUtil
import time
from service.robot.model_config import business_id_map, qa_file_path
from utils.IDEncryptor import IDEncryptor
from xml.etree import ElementTree as eTree
from fuzzywuzzy import process, fuzz
from ES.es_util import EsUtil
from get_config import get_logger_file
import traceback

logger = get_logger_file('robot')
robot_name = "dujia_robot"


def get_similar_question(question, business_id, supplier_id):
    btype = '{}_{}'.format(business_id, supplier_id)
    question_list = []
    result = []
    with open(qa_file_path.format(btype)) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i > 0:
                questions = line.strip().split('\t')[2]
                question_list.append(questions)
    similar_list = process.extract(question, question_list, limit=5)
    for similar in similar_list:
        if similar[1] > 0:
            result.append(similar[0])
    logger.info("get_similar_question similar_list={}".format(similar_list))
    return result


def say_to_robot(m_from, real_from, m_to, real_to, question, business_id, supplier_id):
    try:
        similar_list = []
        ori_similar_list = []
        btype = "{}_{}".format(business_id, supplier_id)
        intent_type = 0
        is_worked = ''
        origin_question = ''
        qa_dict = {}
        right_count = 0
        wrong_count = 0
        question = QuestionFormatUtil.handle_question_format(question, segmentor=None).lower()
        btype_dict, question_dict = get_qa_data(btype)
        qa_in_list = ''
        for word in list(question_dict.keys()):
            qa_in_list += word + ','
        if question:
            ori_similar_list = get_similar_question(question, business_id, supplier_id)
            # 可以用ES快速搜索
            # ori_similar_list = EsUtil.es_similar_question(question, business_id, supplier_id)
            if ori_similar_list and question in ori_similar_list:
                intent_type = 1
                qa_dict = question_dict.get(question)
                origin_question = qa_dict.get("question", "")
                answer = qa_dict.get("answer")
            else:
                qa_dict = get_answer_dict(question, business_id, supplier_id)
                origin_question = qa_dict.get("question")
                answer = qa_dict.get("answer")
        else:
            config_dict = SupplierRobotConfig.select_dict(business_id, supplier_id)
            if config_dict.get("default_questions") == ['']:
                return
            else:
                for dq in config_dict.get("default_questions"):
                    similar_list.append({"question": [dq]})
                answer = ""
        if len(ori_similar_list):
            for s_dict in ori_similar_list:
                similar_list.append(s_dict)
        qtype = str(qa_dict.get("qtype", "-999"))
        qa_dict["origin_question"] = origin_question
        qa_dict["btype"] = btype
        qa_dict["intent_type"] = intent_type
        qa_dict["business_id"] = business_id
        qa_dict["supplier_id"] = supplier_id
        qa_dict["question"] = question
        qa_dict["answer"] = answer
        qa_dict["is_worked"] = is_worked
        qa_dict["right_count"] = right_count
        qa_dict["wrong_count"] = wrong_count
        data = json.dumps(qa_dict, ensure_ascii=False)
        try:
            if question:
                SupplierQaHistory.add_history(business_id, supplier_id, question, answer, origin_question, qtype, btype,
                                              real_to, data, 'qchat_robot', intent_type, is_worked, right_count,
                                              wrong_count)
        except:
            logger.exception("add qa history error question={}, data={}".format(question, json.dumps(qa_dict,
                                                                                                     ensure_ascii=False)))
        message_dict, message_dict_hint = SendMessageUtil.generate_message_dict(m_from, real_from, m_to, real_to,
                                                                                question,
                                                                                answer, business_id, supplier_id,
                                                                                similar_list, mtype="consult")

        logger.info("say_to_robot message_dict={}".format(message_dict))
        ret = SendMessageUtil.send_msg(message_dict)
        if ret:
            time.sleep(0.2)
            SendMessageUtil.send_msg(message_dict_hint)
    except:
        logger.info(
            "qchat info m_from={},m_to={}, question={}, answer={}, business_id={}, supplier_id={}".format(
                m_from, m_to, question, answer, business_id, supplier_id))
        logger.error(traceback.format_exc())


def get_product_data(backupinfo):
    is_first_talk = False
    business_id = ''
    supplier_id = ''
    try:
        backupinfo = json.loads(backupinfo)
        backupinfo_data = {}
        if isinstance(backupinfo, list):
            for bi in backupinfo:
                if bi.get("type") == 50010:
                    backupinfo_data = bi
                elif bi.get("type") == 50001 and bi.get("data", {}).get("isrobot"):
                    is_first_talk = True
                    backupinfo_data = bi
        else:
            backupinfo_data = backupinfo

        bsid_en = backupinfo_data.get("data", {}).get("bsid")
        business_id = business_id_map.get(backupinfo_data.get("data", {}).get("bu"), 0)
        supplier_id = IDEncryptor().decrypt(bsid_en)
    except:
        logger.error(traceback.format_exc())
    return business_id, supplier_id, is_first_talk


def handle_message(value):
    msg = eTree.fromstring(value)
    m_body = msg.find("body")
    msg_type = m_body.get("msgType")
    m_type = msg.get("type")
    m_to = msg.get("to", "")
    m_from = msg.get("from", "")
    real_from = msg.get("realfrom", "")
    real_to = msg.get("realto", "")
    channelid_dict = json.loads(msg.get("channelid", "{}"))
    direct = str(channelid_dict.get("d"))
    question = m_body.text
    business_id, supplier_id, is_first_talk = get_product_data(m_body.get("backupinfo"))
    if robot_name not in real_to and robot_name not in m_to:
        return
    if supplier_id and business_id and (m_type == "consult" or m_type == "note"):
        if robot_name in real_to:
            if direct == 'recv':
                if msg_type == '11':
                    question = ""
                say_to_robot(m_from, real_to, real_from, real_from, question, business_id, supplier_id)


def get_message_queue(robot_message):
    for message in robot_message:
        value = message.value
        try:
            value = json.loads(value)
            if value.get('type') == 'trans':
                continue
            if value.get('type') == 'readmark':
                continue
            value = value.get('m_body')
        except:
            logger.error(traceback.format_exc())
        if isinstance(value, str):
            handle_message(value)
        else:
            handle_message(str(value))


if __name__ == '__main__':
    get_similar_question('退款', 1, 1)
