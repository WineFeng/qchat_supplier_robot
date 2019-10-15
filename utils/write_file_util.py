#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
from utils.tsvh_file import TsvhFileWriter
from ast import literal_eval
import re
from utils.question_format_util import QuestionFormatUtil


class WriteFileUtil:
    def __init__(self):
        pass

    @staticmethod
    def write_to_file(qa_list, file_path, segmentor=None):
        qtype = 0
        keys = "id,qtype,question,answer,provider,source,btypes,supplier_id,business_id"
        w = TsvhFileWriter(file_path, keys=keys)
        qid = 0
        for qa in qa_list:
            if isinstance(qa.get("question"), str):
                questions = literal_eval(qa.get("question"))
            else:
                questions = qa.get("question")
            for q in questions:
                question = QuestionFormatUtil.handle_question_format(q, segmentor)
                ignore_huanhang = re.compile(r"\n")
                ignore_kongge = re.compile(r"\s")
                qtype += 1
                qid += 1
                if question:
                    record = {"qtype": qtype, "question": question.lower(),
                              "answer": ignore_kongge.sub("", ignore_huanhang.sub(";", qa["answer"])),
                              "provider": qa.get("provider", ""), "id": qid,
                              "source": qa.get("source", "local"), "btypes": qa.get("btypes"),
                              "supplier_id": qa.get("supplier_id", ""), "business_id": qa.get("business_id")}
                    w.write(record)
        w.close()
