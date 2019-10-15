#!/usr/bin/env python
# -*- encoding: utf8 -*-

import codecs
import re
import logging


class TsvhFileReader(object):
    def __init__(self, file_name, delimit="\t"):
        self.file_ = file_name
        self.first_line_ = True
        self.delimit_ = delimit
        self.keys_ = []
        self.logger_ = logging.getLogger(self.__class__.__name__)

    def open(self):
        print(self.file_)
        for line in open(self.file_, encoding='utf-8', errors='ignore'):
            # line = line.decode("utf-8")
            line = line.rstrip("\n")
            # values = line.split(self.delimit_)
            values = re.split(self.delimit_, line)
            if self.first_line_:
                self.keys_ = values
                self.first_line_ = False
            else:
                ret = {}
                for i in range(len(self.keys_)):
                    try:
                        k, v = self.parse_tsvh_value(self.keys_[i], values[i])
                    except:
                        if len(self.logger_.handlers) > 0:
                            self.logger_.error("file={}, line={}, keys={}, values={}".format(self.file_, line,
                                                                                             len(self.keys_),
                                                                                             len(values)))
                        else:
                            print("file={}, line={}, keys={}, values={}".format(self.file_,
                                                                                line, len(self.keys_), len(values)))
                    ret[k] = v
                yield ret

    def close(self):
        self.first_line_ = True
        self.keys_ = []

    @staticmethod
    def parse_tsvh_value(key, value):
        m = re.match(r"([^(]+)\(([^)]+)\)", key)
        if m is not None:
            pri_key = m.group(1)
            sub_keys = m.group(2).split(",")
            sub_key_cnt = len(sub_keys)
            list_value = []
            for row in value.split("\x01"):
                cols = row.split("\x02")
                sub_val_cnt = len(cols)
                if sub_val_cnt != sub_key_cnt:
                    # self.logger_.warn("field and value do not match, key= [%s], value= [%s]", key, value)
                    pass
                else:
                    d = {}
                    for i in range(sub_key_cnt):
                        sub_key = sub_keys[i]
                        sub_val = cols[i]
                        d[sub_key] = sub_val
                    list_value.append(d)
            return pri_key, list_value
        else:
            return key, value


class TsvhFileWriter(object):
    def __init__(self, file_name, keys, op="w", delimit="\t"):
        buff_size = 1 * 1024 * 1024
        self.keys_ = keys.split(",")
        self.delimit = delimit
        self.file_handle_ = codecs.open(file_name, op, encoding="utf-8", buffering=buff_size)
        self.file_handle_.write(self.delimit.join(self.keys_))
        self.file_handle_.write("\n")

    def write(self, dict_name):
        a = []
        for k in self.keys_:
            val = ""
            if k in dict_name:
                val = dict_name[k]
            if not isinstance(val, str):
                val = str(val)
            a.append(re.sub(self.delimit, ' ', val))
        self.file_handle_.write(self.delimit.join(a))
        self.file_handle_.write("\n")

    def open(self):
        pass

    def close(self):
        self.file_handle_.close()



