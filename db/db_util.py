#!/usr/bin/env python
# -*- encoding: utf8 -*-

import psycopg2 as pgdb
import psycopg2.extras
from datetime import datetime
import re


def array_to_string(w_lsit):
    return "','".join([re.sub("'|,|;", " ", x) for x in w_lsit])


def sql_escape(s):
    return re.sub("'|;", "", s)


class PgDbDumper:
    array_size_ = 4096
    PORT = '5432'

    @staticmethod
    def parseConnStr(conn_str):
        arr = conn_str.split(":")
        host = arr[0]
        db = arr[1]
        user = arr[2]
        password = arr[3]
        port = PgDbDumper.PORT
        if len(arr) >= 5 and len(arr[4]):
            port = arr[4]
        return host, db, user, password, port

    @staticmethod
    def getconn(conn_str):
        host, database, user, password, port = PgDbDumper.parseConnStr(conn_str)
        conn = pgdb.connect(host=host, database=database, user=user, password=password, port=port)
        conn.autocommit = True
        return conn

    @staticmethod
    def update(conn_str, sql):
        conn = PgDbDumper.getconn(conn_str)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        return rowcount

    @staticmethod
    def update_args(conn_str, sql, args):
        conn = PgDbDumper.getconn(conn_str)
        cursor = conn.cursor()
        cursor.execute(sql, args)
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        return rowcount

    @staticmethod
    def select_dict(conn_str, sql):
        conn = PgDbDumper.getconn(conn_str)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.arraysize = PgDbDumper.array_size_
        cursor.execute("SET standard_conforming_strings=on;")
        cursor.execute(sql)
        rs = cursor.fetchall()
        result = []
        for row in rs:
            result.append(
                {k: v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v for k, v in list(row.items())})
        return result

    @staticmethod
    def select_dict_args(conn_str, sql, args):
        conn = PgDbDumper.getconn(conn_str)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.arraysize = PgDbDumper.array_size_
        cursor.execute("SET standard_conforming_strings=on;")
        cursor.execute(sql, args)
        rs = cursor.fetchall()
        result = []
        for row in rs:
            result.append(
                {k: v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v for k, v in list(row.items())})
        return result

    @staticmethod
    def query_one_column_list(conn_str, sql):
        result = []
        conn = PgDbDumper.getconn(conn_str)
        cursor = conn.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        for row in rs:
            result.append(row[0])
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def select_dict_count(conn_str, count_sql, args):
        conn = PgDbDumper.getconn(conn_str)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.arraysize = PgDbDumper.array_size_
        cursor.execute("SET standard_conforming_strings=on;")
        cursor.execute(count_sql, args)
        rs = cursor.fetchall()
        count = 0
        for row in rs:
            print(row)
            count = row
        return count
