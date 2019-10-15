#!/usr/bin/env bash
source /home/jingyu.he/venv/bin/activate
ps aux | grep uwsgi_dl | grep -v "grep" | awk -F' ' '{print $2}'| xargs -I {} sudo kill -9 {}
sleep 2
uwsgi --ini /root/qchat_supplier_robot/conf/uwsgi_dl.ini