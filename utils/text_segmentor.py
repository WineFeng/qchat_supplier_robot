#!/usr/bin/env python
# -*- encoding: utf8 -*-

import jieba.posseg as posseg
import time


class TextSegmentor:
    def __init__(self):
        self.posseg = posseg

    def segment(self, text):
        res = []
        for pair in self.posseg.cut(text):
            res.append([pair.word, pair.flag])
        print(res)
        return res


if __name__ == '__main__':
    now = time.time()
    ts = TextSegmentor().segment("周杰伦是什么")
    print("done")
