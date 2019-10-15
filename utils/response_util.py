#!/usr/bin/env python
# -*- encoding: utf8 -*-


import json
from flask import Response


RESPONSE_STATUS = "status"
RESPONSE_MSG = "message"
RESPONSE_DATA = "data"


def common_response_dict(status=0, message=None, data=None, **kwargs):
    ret = {RESPONSE_STATUS: status}
    if message is not None:
        ret[RESPONSE_MSG] = message
    if data is not None:
        ret[RESPONSE_DATA] = data
    ret.update(kwargs)
    return ret


def common_response(status=0, message=None, data=None, **kwargs):
    response_dict = common_response_dict(status, message, data, **kwargs)
    return Response(json.dumps(response_dict, ensure_ascii=False), 
                    mimetype="application/json",
                    content_type='application/json;charset=UTF-8')

