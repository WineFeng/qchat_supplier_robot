#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append("././")
from flask import request, Blueprint
from utils.request_util import RequestUtil
from service.robot.say_to_robot import get_message_queue
from utils.response_util import common_response
from get_config import get_logger_file
import traceback

logger = get_logger_file('api')

say_robot = Blueprint(__file__, 'SayToRobot', template_folder='templates', url_prefix='/qchat_robot')


@say_robot.route('/robot_message', methods=['GET', 'POST'])
def get_message_queue():
    try:
        args = RequestUtil.get_request_args(request)
        robot_message = args.get('robot_message')
        if robot_message:
            get_message_queue(robot_message)
            logger.info("get_message_queue robot_message={}".format(robot_message))
            return common_response(status=0, data=None, message='success')
        else:
            return common_response(status=1, data=None,
                                   message='please input business_id, and supplier_id')
    except:
        logger.info("get_message_queue failed")
        logger.error(traceback.format_exc())
