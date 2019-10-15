#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys

sys.path.append('././')

from db.db_connstr import conn_str
from db.db_util import PgDbDumper, array_to_string, sql_escape
import re
from get_config import get_logger_file

logger = get_logger_file('sql')


class SupplierRobotConfig:
    def __init__(self):
        pass

    @staticmethod
    def select_dict(business_id, supplier_id):
        sql = """
        select id, business_id, supplier_id, default_questions, create_time, update_time, update_user, status from supplier_robot_config where business_id = {business_id} and supplier_id = {supplier_id}
        """.format(business_id=business_id, supplier_id=supplier_id)
        config_list = PgDbDumper.select_dict(conn_str, sql)
        logger.info("SupplierRobotConfig table select_dict ={}".format(config_list))
        if config_list:
            config = config_list[0]
            return config
        else:
            return {}

    @staticmethod
    def update(business_id, supplier_id, default_questions, update_user, status):
        if business_id and supplier_id:
            sql = '''
            insert into supplier_robot_config(business_id, supplier_id, default_questions, update_user, status)
            values({business_id}, {supplier_id},  ARRAY['{default_questions}'], '{update_user}', {status}) 
            on conflict (business_id, supplier_id) do update set  default_questions=ARRAY['{default_questions}'], 
            update_user='{update_user}', status={status}, update_time=now() 
            '''.format(business_id=business_id, supplier_id=supplier_id,
                       default_questions=array_to_string(default_questions), update_user=update_user, status=status)
            n = PgDbDumper.update(conn_str, sql)
            logger.info("SupplierRobotConfig table update ={}".format(default_questions))
            return n
        return 0


class SupplierQaData:
    def __init__(self):
        pass

    @staticmethod
    def select_byid(qaid):
        sql = """
            select id, business_id, supplier_id, question, answer, status, create_time, update_time, update_user from supplier_qa_data where id = {}
            """.format(qaid)
        qa_list = PgDbDumper.select_dict(conn_str, sql)
        logger.info("SupplierQaData table select_byid ={}".format(qa_list))
        if qa_list:
            return qa_list[0]
        else:
            return {}

    @staticmethod
    def select_list(business_id, supplier_id):
        sql = """
        select id, business_id, supplier_id, question, answer, status, create_time, update_time, update_user from supplier_qa_data where business_id = {} and supplier_id = {}
        """.format(business_id, supplier_id)
        qa_list = PgDbDumper.select_dict(conn_str, sql)
        logger.info("SupplierQaData table select_list ={}".format(qa_list))
        if qa_list:
            for qa in qa_list:
                qa["source"] = "db"
            return qa_list
        else:
            return []

    @staticmethod
    def update(qaid, business_id, supplier_id, question, answer, status, update_user):
        if len(qaid) == 0:
            sql = """
            insert into supplier_qa_data(business_id, supplier_id, question, answer, update_user) values({business_id}, {supplier_id}, ARRAY['{question}'], '{answer}', '{update_user}')
            """.format(business_id=business_id, supplier_id=supplier_id, question=array_to_string(question),
                       answer=sql_escape(answer), update_user=update_user)
        else:
            sql = """
            update supplier_qa_data set business_id={business_id}, supplier_id={supplier_id}, question=ARRAY['{question}'], answer='{answer}'=}', status={status}, update_user='{update_user}' where id = {id}""".format(
                id=qaid, business_id=business_id, supplier_id=supplier_id, question=array_to_string(question),
                answer=sql_escape(answer), status=status, update_user=update_user)
        logger.info("SupplierQaData table update ={}".format(dict(question=question, answer=answer)))
        n = PgDbDumper.update(conn_str, sql)
        return n

    @staticmethod
    def select_btype():
        sql = """
        select distinct business_id, supplier_id from supplier_qa_data  where status=1 
        """
        ret = []
        for s in PgDbDumper.select_dict(conn_str, sql):
            ret.append((int(s.get("business_id")), int(s.get("supplier_id"))))
        logger.info("SupplierQaData table select_btype ={}".format(ret))
        return ret

    @staticmethod
    def select_to_es(business_id, supplier_id):
        sql = """
        select id, business_id, supplier_id, question, answer from supplier_qa_data where business_id = {business_id} and supplier_id = {supplier_id}""".format(
            business_id=business_id, supplier_id=supplier_id)
        qa_list = PgDbDumper.select_dict(conn_str, sql)
        logger.info("SupplierQaData table select_to_es ={}".format(qa_list))
        if qa_list:
            return qa_list
        else:
            return []


class SupplierQaHistory:
    def __init__(self):
        pass

    @staticmethod
    def add_history(business_id, supplier_id, question, answer, origin_question, qtype, btype,
                    username='aaa', data=None, robot=None, intent_type=0, is_worked=0, right_count=0,
                    wrong_count=0):
        sql = """
        insert into supplier_qa_history(business_id,supplier_id,question, answer,origin_question, qtype,btype, username, create_time, qa_dict, robot,intent_type,is_worked,right_count,wrong_count)
        values('{business_id}','{supplier_id}','{question}', '{answer}','{origin_question}','{qtype}', '{btype}', '{username}', now(), E'{qa_dict}', '{robot}','{intent_type}','{is_worked}','{right_count}','{wrong_count}')
        """.format(business_id=business_id, supplier_id=supplier_id, question=question, answer=answer,
                   origin_question=origin_question, qtype=qtype, btype=btype, username=username,
                   qa_dict=re.sub("'", "\\'", data), robot=robot if robot else btype, intent_type=intent_type,
                   is_worked=is_worked, right_count=right_count,
                   wrong_count=wrong_count)
        PgDbDumper.update(conn_str, sql)
        logger.info("SupplierQaHistory table add_history ={}".format(
            dict(business_id=business_id, supplier_id=supplier_id, queetion=question, answer=answer)))

    @staticmethod
    def select_feedback_dict(limit, offset, start_time, end_time, intent_type, status,
                             is_worked, business_id, supplier_id):

        count_sql = """
        select count(*) from supplier_qa_history where 1=1
        """
        sql = """
        select id,create_time,business_id, supplier_id, question, answer,origin_question,product_id,intent_type,is_worked,status,update_time 
        from supplier_qa_history 
        where 1=1 and answer <>''
        """
        if business_id and supplier_id:
            sql += "and business_id= %(business_id)s and supplier_id = %(supplier_id)s "
            count_sql += "and business_id= %(business_id)s and supplier_id = %(supplier_id)s "
        if start_time:
            sql += " and substr(cast(create_time as varchar),1,10)>=%(start_time)s "
            count_sql += " and substr(cast(create_time as varchar),1,10)>=%(start_time)s "
        if end_time:
            sql += "  and substr(cast(create_time as varchar),1,10)<=%(end_time)s"
            count_sql += "  and substr(cast(create_time as varchar),1,10)<=%(end_time)s"
        if intent_type:  # 意图类型
            sql += " and intent_type= %(intent_type)s"
            count_sql += " and intent_type= %(intent_type)s"
        if is_worked:  # 用户反馈
            sql += " and is_worked = %(is_worked)s "
            count_sql += " and is_worked = %(is_worked)s "
        if status:  # 处理状态
            sql += " and status= %(status)s "
            count_sql += " and status= %(status)s "
        sql += "  order  by create_time desc limit %(limit)s offset %(offset)s"
        args = {'business_id': "{}".format(business_id), 'supplier_id': "{}".format(supplier_id),
                'start_time': "{}".format(start_time), 'end_time': '{}'.format(end_time),
                'intent_type': "{}".format(intent_type), 'status': "{}".format(status),
                'is_worked': "{}".format(is_worked), 'limit': "{}".format(limit), 'offset': "{}".format(offset)}
        select_dict = PgDbDumper.select_dict_args(conn_str, sql, args)
        count = PgDbDumper.select_dict_count(conn_str, count_sql, args)
        logger.info("SupplierQaHistory table select_feedback_dict ={} {}".format(select_dict, count))
        return select_dict, count

    @staticmethod
    def update_feedback(qid, business_id, supplier_id, answer, intent_type, status, update_user):
        if qid:
            sql = """
            update supplier_qa_history set business_id=%(business_id)s, supplier_id=%(supplier_id)s, answer=%(answer)s, update_time=now(), status=%(status)s, intent_type=%(intent_type)s,update_user=%(update_user)s 
            where id = %(qid)s and business_id=%(business_id)s and supplier_id=%(supplier_id)s"""
            args = {'qid': qid, 'business_id': business_id, 'supplier_id': supplier_id,
                    'answer': answer, 'status': status, 'intent_type': intent_type, 'update_user': update_user}
            n = PgDbDumper.update_args(conn_str, sql, args)
            logger.info("SupplierQaHistory table update_feedback ={}".format(
                dict(supplier_id=supplier_id, business_id=business_id, qid=qid, answer=answer)))
            return n

    @staticmethod
    def select_byid(fbid):
        sql = """
            select robot from supplier_qa_history where id = {id}""".format(id=fbid)
        qa_list = PgDbDumper.select_dict(conn_str, sql)
        logger.info("SupplierQaHistory table select_byid ={}".format(qa_list))
        if qa_list:
            return qa_list[0]
        else:
            return {}

    @staticmethod
    def select_by_question(question, answer):
        sql = """
            select id  from supplier_qa_history where question='{question}'and answer='{answer}' order by id desc limit 1""".format(
            question=question, answer=answer)
        qa_list = PgDbDumper.select_dict(conn_str, sql)
        logger.info("SupplierQaHistory table select_by_question ={}".format(qa_list))
        if qa_list:
            return qa_list[0]
        else:
            return {}

    @staticmethod
    def get_worked_status(qid):
        worked_status = ''
        select_list = []
        if qid:
            sql = """select is_worked from supplier_qa_history where id={id}""".format(id=qid)
            select_list = PgDbDumper.select_dict(conn_str, sql)
        for status_dict in select_list:
            worked_status = status_dict.get("is_worked")
        logger.info("SupplierQaHistory table get_worked_status ={}".format(dict(qid=qid, abscount=worked_status)))
        return worked_status

    @staticmethod
    def get_abscount(qid):
        abscount = 0
        if qid:
            sql = """
            select ABS(right_count) + ABS(wrong_count) from supplier_qa_history where id={id} limit 1""".format(
                id=qid)
            count_list = PgDbDumper.query_one_column_list(conn_str, sql)
            for count in count_list:
                abscount = count
        logger.info("SupplierQaHistory table get_abscount ={}".format(dict(qid=qid, abscount=abscount)))
        return abscount

    @staticmethod
    def add_right_wrong(qid, field, is_worked, business_id, supplier_id):
        if qid:
            sql = """
            update supplier_qa_history set {field}={field}+ 1,is_worked='{is_worked}' where business_id={business_id} and supplier_id={supplier_id} and  id = {id}""".format(
                field=field, is_worked=is_worked, business_id=business_id, supplier_id=supplier_id, id=qid)
            n = PgDbDumper.update(conn_str, sql)
            logger.info("SupplierQaHistory table add_right_wrong ={}".format(
                dict(qid=qid, business_id=business_id, supplier_id=supplier_id)))
            return n

    @staticmethod
    def update_yn(qid, business_id, supplier_id, is_worked):
        if qid:
            sql = """
            update supplier_qa_history set business_id=%(business_id)s, supplier_id=%(supplier_id)s, update_time=now(), is_worked= %(is_worked)s
            where id = %(qid)s and business_id=%(business_id)s and supplier_id=%(supplier_id)s"""
            args = {'qid': qid, 'business_id': business_id, 'supplier_id': supplier_id, 'is_worked': is_worked}
            n = PgDbDumper.update_args(conn_str, sql, args)
            logger.info("SupplierQaHistory table update_yn ={}".format(
                dict(qid=qid, business_id=business_id, supplier_id=supplier_id)))
            return n

    @staticmethod
    def ignore_feedback(qid, business_id, supplier_id, status, update_user):
        if qid:
            sql = """
            update supplier_qa_history set business_id=%(business_id)s, supplier_id=%(supplier_id)s,  update_time=now(), status=%(status)s,update_user=%(update_user)s 
            where id = %(qid)s and business_id=%(business_id)s and supplier_id=%(supplier_id)s"""
            args = {'qid': qid, 'business_id': business_id, 'supplier_id': supplier_id, 'status': status,
                    'update_user': update_user}
            n = PgDbDumper.update_args(conn_str, sql, args)
            logger.info("SupplierQaHistory table ignore_feedback ={}".format(
                dict(qid=qid, business_id=business_id, supplier_id=supplier_id)))
            return n


if __name__ == '__main__':
    print(SupplierRobotConfig.select_dict(0, 0))
    print(SupplierQaData.select_list(0, 0))
