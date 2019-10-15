#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append('././')
from db.get_database_data import SupplierQaData
from ES.es_util import EsUtil


class WriteToES:
    def __init__(self):
        pass

    @staticmethod
    def write_to_es(business_id, supplier_id):
        es_index, es_client = EsUtil.create_es_index(business_id, supplier_id)
        qa_list = SupplierQaData.select_to_es(business_id, supplier_id)
        qflag = 0
        qid = 0
        for qa in qa_list:
            answer = qa.get("answer")
            businessId = qa.get("business_id")
            supplierId = qa.get("supplier_id")
            questions = qa.get("question")
            qflag += 1
            if questions == [""]:
                pass
            else:
                for question in questions:
                    question_list = []
                    question_list.append(question)
                    qid += 1
                    record = dict(qflag=qflag, question=question_list, answer=answer, business_id=businessId,
                                  supplier_id=supplierId)
                    es_client.index(index=es_index, doc_type='qalist', id=qid, body=record)
        return es_client

    @staticmethod
    def delete_es_qa(business_id, supplier_id):
        es_index, es_client = EsUtil.create_es_index(business_id, supplier_id)
        es_client.indices.delete(index=es_index)
