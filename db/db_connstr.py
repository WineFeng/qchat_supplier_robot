#!/usr/bin/env python
# -*- encoding: utf8 -*-

from get_config import get_config_file

config = get_config_file()

HOST = config["postgresql"]["HOST"]
PASSWORD = config["postgresql"]["PASSWORD"]
USER = config["postgresql"]["USER"]
DATABASE = config["postgresql"]["DATABASE"]
PORT = config["postgresql"]["PORT"]
conn_str = "{}:{}:{}:{}:{}".format(HOST, DATABASE, USER, PASSWORD, PORT)
