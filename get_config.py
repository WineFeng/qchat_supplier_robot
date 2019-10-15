#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys
import os
import configparser
import logging.config

base_dir = os.path.abspath(os.path.dirname(__file__))

PROD = False
for arg in sys.argv:
    if "conf=prod" in arg:
        PROD = True
        break


def get_logger_file(name):
    project_dir = os.path.dirname(__file__)
    logging.config.fileConfig(project_dir + "/conf/logging.ini")
    return logging.getLogger(name)


def get_config_file():
    project_dir = os.path.dirname(__file__)
    conf_path = project_dir + '/conf/config.ini'
    config = configparser.ConfigParser()
    config.read(conf_path, 'utf-8')
    return config


if __name__ == '__main__':
    print(os.path.dirname(__file__))
    print(os.path.realpath(__file__))
    config = get_config_file()
    get_logger_file("sql")
