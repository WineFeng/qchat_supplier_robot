#!/usr/bin/env python
# -*- encoding: utf8 -*-


from service.robot.web_api import qchat_robot
from service.robot.robot_api import say_robot
from flask import Flask, redirect

app = Flask(__name__)
app.register_blueprint(qchat_robot)
app.register_blueprint(say_robot)


@app.route('/healthcheck.html')
def health_check():
    return 'ok'


# @app.route('/favicon.ico')
# def favicon():
#     return redirect("http://0.0.0.0:8080/favicon.ico")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8023, debug=True)
