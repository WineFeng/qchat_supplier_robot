#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
import json
import requests
import uuid
from db.get_database_data import SupplierQaHistory
from xml.sax.saxutils import escape
from get_config import get_config_file

config = get_config_file()

SEND_THIRDMESSAGE = config["qchat"]["SEND_THIRDMESSAGE"]
API_URL = config["qchat"]["API_URL"]


class SendMessageUtil:
    def __init__(self):
        pass

    @staticmethod
    def send_msg(message_dict):
        url = SEND_THIRDMESSAGE
        data = json.dumps(message_dict)
        ret = False
        headers = {"content-type": "application/json"}
        r = requests.post(url, data=data, headers=headers, stream=True)
        if r.status_code == 200:
            ret = True
            return ret
        else:
            return ret

    @staticmethod
    def get_message_dict(m_from, real_from, m_to, real_to, msg_type, extend_info, mtype='consult'):
        channelid = {"d": "recv", "cn": "consult", "usrType": "rbt"}
        message = "<message from='{m_to}' to='{m_from}' type='{mtype}' realfrom='{m_to}' " \
                  "realto='{real_from}' channelid='{channelid}'>" \
                  "<body id='{uuid}' msgType='{msg_type}' extendInfo='{extend_info}'>版本过低，请升级到最新版本</body>" \
                  "</message>".format(m_from=m_from, real_from=real_from, m_to=m_to, real_to=real_to,
                                      channelid=json.dumps(channelid), mtype=mtype,
                                      uuid=str(uuid.uuid1()) + '_robot_msg', msg_type=msg_type,
                                      extend_info=json.dumps(extend_info))
        message_dict = {"from": m_from, "to": m_to, "message": message}
        return message_dict

    @staticmethod
    def generate_message_dict(m_from, real_from, m_to, real_to, question, answer, business_id, supplier_id,
                              similar_list, mtype="consult"):
        items = []
        qid = SupplierQaHistory.select_by_question(question, answer).get("id")
        list_area = {"type": "list", "style": {"defSize": 5}}
        msg_type = '65536'
        bottom = []
        word_limit = {"words": 100, "lines": 6}
        if similar_list:
            for qa_dict in similar_list:
                question = qa_dict.get("question")[0]
                items.append(
                    {"text": question,
                     "event": {"type": "interface", "url": qa_dict.get("url", ""), "msgText": question}})
        else:
            items = []
        list_area["items"] = items
        y_url = "{}/yn_feedback?id={}&is_worked=1&business_id={}&supplier_id={}&m_from={}&realfrom={}&m_to={}&realto={}".format(
            API_URL, qid, business_id, supplier_id, m_from, real_from, m_to, real_to)
        n_url = "{}/yn_feedback?id={}&is_worked=0&business_id={}&supplier_id={}&m_from={}&realfrom={}&m_to={}&realto={}".format(
            API_URL, qid, business_id, supplier_id, m_from, real_from, m_to, real_to)
        bottom.append({"id": 1, "text": '有用', "url": y_url})
        bottom.append({"id": 0, "text": '没用', "url": n_url})
        if answer:
            if len(items) > 0:
                list_tips = "您是否还想问?"
            else:
                list_tips = ""
            extend_info = {"question": question, "content": answer, "listTips": list_tips, "listArea": list_area,
                           'bottom': bottom, 'word_limit': word_limit}
        else:
            list_tips = "您是否遇到了以下问题?"
            extend_info = {"question": question, "content": answer, "listTips": list_tips, "listArea": list_area}

        msg_type_hint = '65537'
        extend_info_hint = {"hints": [{"text": "没有解决您的问题？", "event": {"url": "", "msgText": "", "type": "text"}},
                                      {"text": "找人工客服", "event": {"url": "", "msgText": "找人工客服", "type": "interface"}}]}
        return (SendMessageUtil.get_message_dict(m_from, real_from, m_to, real_to, msg_type, extend_info, mtype=mtype),
                SendMessageUtil.get_message_dict(m_from, real_from, m_to, real_to, msg_type_hint, extend_info_hint,
                                                 mtype=mtype))

    @staticmethod
    def send_yn_answer(m_from, real_from, m_to, real_to, is_worked):
        msg_type = 1
        mtype = 'consult'
        extend_info = ''
        answer = ""
        channelid = {"d": "recv", "cn": "consult", "usrType": "rbt"}
        if is_worked == '1':
            answer = "感谢你的大赞,我会继续努力的~"

        elif is_worked == '0':
            answer = "感谢你的反馈,我会好好学习的~"
        message = "<message from='{m_from}' to='{m_to}' type='{mtype}' realfrom='{real_from}' " \
                  "realto='{real_to}' channelid='{channelid}' qchatid='5'>" \
                  "<body id='{uuid}' msgType='{msg_type}' extendInfo='{extend_info}'>'{answer}'</body>" \
                  "</message>".format(m_from=m_from, real_from=real_from, m_to=m_to, real_to=real_to,
                                      channelid=json.dumps(channelid),
                                      uuid=str(uuid.uuid1()) + '_dl_apps', msg_type=msg_type, mtype=mtype,
                                      extend_info=escape(json.dumps(extend_info)), answer=answer)
        message_dict = {"from": m_from, "to": m_to, "message": message}
        SendMessageUtil.send_msg(message_dict)
