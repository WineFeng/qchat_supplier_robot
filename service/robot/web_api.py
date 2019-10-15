#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
from flask import request, Blueprint
import os
from utils.request_util import RequestUtil
from utils.IDEncryptor import IDEncryptor
from db.get_database_data import SupplierQaData, SupplierQaHistory, SupplierRobotConfig
from utils.response_util import common_response
from service.robot.qa_data import write_qa_data, delete_qa_data
from utils.send_message_util import SendMessageUtil
from get_config import get_logger_file
import traceback

logger = get_logger_file('api')

qchat_robot = Blueprint(__file__, 'QcAdmin', template_folder='templates', url_prefix='/qchat_robot')

idEncryptor = IDEncryptor()


@qchat_robot.route('/config', methods=['GET', 'POST'])
def get_config():
    try:
        args = RequestUtil.get_request_args(request)
        business_id = args.get('business_id')
        supplier_id = args.get('supplier_id')
        if business_id and supplier_id:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                data = SupplierRobotConfig.select_dict(business_id, supplier_id)
                return common_response(status=0, data=data, message='success')
            except:
                logger.error(
                    "datebase get_config business_id={},supplier_id={} failed ".format(business_id, supplier_id))
        else:
            return common_response(status=1, data={"business_id": business_id, "supplier_id": supplier_id},
                                   message='please input business_id, and supplier_id')
    except:
        logger.error("api config  failed")
        logger.error(traceback.extract_stack())


@qchat_robot.route('/update_config', methods=['GET', 'POST'])
def update_config():
    try:
        args = RequestUtil.get_request_args(request)
        business_id = args.get('business_id', '0')
        supplier_id = args.get('supplier_id')
        operator = args.get('operator', '').strip()
        status = args.get('status', '1').strip()
        default_questions = args.get('default_questions')
        if not isinstance(default_questions, list):
            default_questions = (default_questions or '').split(",")
        default_questions = [x for x in [x.strip() for x in default_questions] if len(x)]
        if business_id and supplier_id:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                SupplierRobotConfig.update(business_id, supplier_id, default_questions, operator, status)
                return common_response(status=0, data=None, message='success')
            except:
                logger.erro("database update_config failed business_id={},supplier={}".format(business_id, supplier_id))
        else:
            return common_response(status=1, data=None, message=' please input business_id and supplier_id')
    except:
        logger.error("api update_config failed")
        logger.error(traceback.format_exc())


@qchat_robot.route('/qalist', methods=['GET', 'POST'])
def get_qa_data_list():
    try:
        args = RequestUtil.get_request_args(request)
        business_id = args.get('business_id', '0')
        supplier_id = args.get('supplier_id')
        if business_id and supplier_id:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                data = SupplierQaData.select_list(business_id, supplier_id)
                return common_response(status=0, data=data, message='success')
            except:
                logger.error("database get qa_{business_id}_{supplier_id} list failed".format(business_id=business_id,
                                                                                              supplier_id=supplier_id))
        else:
            return common_response(status=1, data=None, message=' please input business_id and supplier_id')
    except:
        logger.error("api qalist failed ")
        logger.error(traceback.format_exc())


@qchat_robot.route('/update_qa', methods=['GET', 'POST'])
def update_qa_data():
    try:
        args = RequestUtil.get_request_args(request)
        qaid = args.get('id', '').strip()
        business_id = args.get('business_id', '').strip()
        supplier_id = args.get('supplier_id', '').strip()
        question = args.get('question')
        if not isinstance(question, list):
            question = (question or '').split(",")
            question = [x for x in [x.strip() for x in question] if len(x)]
        answer = args.get('answer', '').strip()
        status = args.get('status', '1').strip()
        operator = args.get('operator', '').strip()
        if business_id and supplier_id:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                n = SupplierQaData.update(qaid, business_id, supplier_id, question, answer, status, operator)
                if n > 0:
                    data = SupplierQaData.select_list(business_id, supplier_id)
                    if data:
                        write_qa_data(business_id, supplier_id)
                    else:
                        delete_qa_data(business_id, supplier_id)
                    return common_response(status=0, data=None, message='success')
                else:
                    return common_response(status=1, data=None, message='update data failded')
            except:
                logger.error("database update_qa business_id={},supplier_id={} failed".format(business_id, supplier_id))
        else:
            return common_response(status=1, data=None, message='please input business_id and supplier_id')
    except:
        logger.error("api update_qa failed")
        logger.error(traceback.format_exc())


@qchat_robot.route('/feedback', methods=['GET', 'POST'])
def get_feedback():
    try:
        args = RequestUtil.get_request_args(request)
        business_id = args.get('business_id', '')
        supplier_id = args.get('supplier_id', '')
        start_time = args.get('start_time', '')
        end_time = args.get('end_time', '')
        offset = int(args.get("offset", 0))
        limit = int(args.get("limit", 20))
        intent_type = args.get('intent_type', 0)
        status = args.get('status', 0)
        is_worked = args.get('is_worked', '')
        if business_id and supplier_id:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                data, total = SupplierQaHistory.select_feedback_dict(limit, offset, start_time, end_time, intent_type,
                                                                     status,
                                                                     is_worked, business_id, supplier_id)
                count = total.get("count")
                return common_response(status=0, data=data, count=count, message='success')
            except:
                logger.error("database select_feedback_dict failed business_id={}, supplier_id={}".format(business_id,
                                                                                                          supplier_id))
        else:
            return common_response(status=1, data=None, count=0,
                                   message='please input business_id, and supplier_id')
    except:
        logger.error("api feedback failed")
        logger.error(traceback.format_exc())


@qchat_robot.route('/update_feedback', methods=['GET', 'POST'])
def update_feedback():
    try:
        args = RequestUtil.get_request_args(request)
        qid = args.get('id', '')
        business_id = args.get('business_id', '').strip()
        supplier_id = args.get('supplier_id', '').strip()
        answer = args.get('answer', '').strip()
        status = 1
        intent_type = args.get("intent_type", 0)
        operator = args.get('operator', '').strip()
        if business_id and supplier_id and qid and intent_type and answer:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                n = SupplierQaHistory.update_feedback(qid, business_id, supplier_id, answer, intent_type, status,
                                                      operator)
                print(n)
                if n:
                    return common_response(status=0, data=None, message='success')
                else:
                    return common_response(status=1, data=None, message='update data failded')
            except:
                logger.error("database update_feedback failed business_id={},supplier_id={},qid={}".format(business_id,
                                                                                                           supplier_id,
                                                                                                           qid))

        else:
            return common_response(status=1, data=None, message='please input business_id and supplier_id')
    except:
        logger.error("api update_feedback failed")
        logger.error(traceback.format_exc())


@qchat_robot.route('/ignore_feedback', methods=['GET', 'POST'])
def ignore_feedback():
    try:
        args = RequestUtil.get_request_args(request)
        qid = args.get('id', '')
        business_id = args.get('business_id', '').strip()
        supplier_id = args.get('supplier_id', '').strip()
        status = 1
        operator = args.get('operator', '').strip()
        if business_id and supplier_id and qid:
            supplier_id = idEncryptor.decrypt(supplier_id)
            try:
                n = SupplierQaHistory.ignore_feedback(qid, business_id, supplier_id, status, operator)
                if n:
                    return common_response(status=0, data=None, message='success')
                else:
                    return common_response(status=1, data=None, message='update data failded')
            except:
                logger.error("database ignore_feedback failed business_id={},supplier_id={},qid={}".format(business_id,
                                                                                                           supplier_id,
                                                                                                           qid))
        else:
            return common_response(status=1, data=None, message='please input id,business_id and supplier_id')
    except:
        logger.error("api ignore_feedback failed")
        logger.error(traceback.format_exc())



@qchat_robot.route('/yn_feedback', methods=['GET', 'POST'])
def yes_no_api():
    try:
        args = RequestUtil.get_request_args(request)
        is_worked = args.get("is_worked")
        question = args.get("question", "")
        answer = args.get("answer", "")
        qid = args.get("id", '')
        business_id = args.get('business_id', '')
        supplier_id = args.get('supplier_id', '')
        m_from = args.get("m_from", "")
        realfrom = args.get("realfrom", "")
        realto = args.get("realto", "")
        m_to = args.get("m_to", "")
        field = ''
        if qid == None:
            try:
                qid = SupplierQaHistory.select_by_question(question, answer).get("id")
            except:
                logger.error("database select_qid_by_question failed")
        abscount = SupplierQaHistory.get_abscount(qid)
        worked_status = SupplierQaHistory.get_worked_status(qid)
        data = {"id": qid, "is_worked": worked_status, "count": abscount}
        if abscount == 0:
            if qid and is_worked and business_id and supplier_id and m_from and realfrom and realto and m_to:
                if is_worked == '1':
                    field = "right_count"
                elif is_worked == '0':
                    field = "wrong_count"
                n1 = SupplierQaHistory.add_right_wrong(qid, field, is_worked, business_id, supplier_id)
                n2 = SupplierQaHistory.update_yn(qid, business_id, supplier_id, is_worked)
                data = {"id": qid, "is_worked": is_worked, "count": abscount}
                if n1 > 0 and n2 > 0:
                    SendMessageUtil.send_yn_answer(m_from=m_from, real_from=realfrom, m_to=m_to, real_to=realto,
                                                   is_worked=is_worked)
                    return common_response(status=0, data=data, message='success')

                else:
                    return common_response(status=1, data=data, message='update data failded')

            else:
                return common_response(status=1, data=None,
                                       message='failded,please input qid ,is_worked, business_id, supplier_id')
        else:
            return common_response(status=1, data=data,
                                   message='You have already operated!')
    except:
        logger.error("api yn_feedback failed")
        logger.error(traceback.format_exc())

