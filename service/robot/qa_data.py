#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
from db.get_database_data import SupplierQaData
from service.robot.model_config import qa_file_path
from utils.write_file_util import WriteFileUtil
from ES.write_to_es import WriteToES
import os
import traceback
from get_config import get_logger_file

logger = get_logger_file('robot')


def write_qa_data(business_id, supplier_id):
    try:
        qa_list = []
        qa_list.extend(SupplierQaData.select_list(business_id, supplier_id))
        btype = '{}_{}'.format(business_id, supplier_id)
        for qa in qa_list:
            qa["btype"] = [btype]
            qa["business_id"] = business_id
            qa["supplier_id"] = supplier_id
        qa_file = qa_file_path.format(btype)
        WriteFileUtil.write_to_file(qa_list=qa_list, file_path=qa_file, segmentor=None)
        WriteToES.write_to_es(business_id, supplier_id)
        logger.info("write_qa_data qa_list={},qa_file={}".format(qa_list, qa_file))
    except:
        logger.info("write to  qa_{}_{}.txt failed".format(business_id, supplier_id))
        logger.error(traceback.format_exc())


def delete_qa_data(business_id, supplier_id):
    btype = "{}_{}".format(business_id, supplier_id)
    os.remove(qa_file_path.format(btype))
    WriteToES.delete_es_qa(business_id, supplier_id)

