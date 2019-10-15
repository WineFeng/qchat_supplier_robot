#!/usr/bin/env python
# -*- encoding: utf8 -*-
import re

chinese_pattern = re.compile("[\\u4e00-\\u9fa5]+")
ignore_pattern = re.compile(r",|，|。|\.|\?|？|!|！|\s|\\\\n|\t")
en_ignore_pattern = re.compile(r",|，|。|\.|\?|？|!|！|\\\\n|\t")


class QuestionFormatUtil:
    def __init__(self):
        pass

    @staticmethod
    def segment_question(q, segmentor):
        result = []
        for word, wtype in segmentor.segment(q):
            if wtype == 'x' or word in ["吗", "么"]:
                continue
            result.append(word)
        q = " ".join(result)
        return q

    @staticmethod
    def handle_question_format(q, segmentor=None):
        if not isinstance(q, str):
            q = str(q)
        if segmentor:
            q = QuestionFormatUtil.segment_question(q, segmentor)
        else:
            if chinese_pattern.search(q) is None:
                q = en_ignore_pattern.sub("", q)
            else:
                q = QuestionFormatUtil.format_question(q)
        return q

    @staticmethod
    def format_question(question):
        question = ignore_pattern.sub("", question)
        return question
