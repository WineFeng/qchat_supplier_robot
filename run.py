#!/usr/bin/env python
# -*- encoding: utf8 -*-

import socket
import os
from get_config import PROD, base_dir, get_config_file
from service.robot.qa_data import write_qa_data
from service.robot.train_qa import qa_train
from db.get_database_data import SupplierQaData
from service.robot.model_config import qa_file_path, result_dir, project_dir, app_dir
from service.cnn.question_model import get_last_checkpoint_dir

config = get_config_file()
hosts = config["hosts"]["HOSTS"]

if PROD:
    conf = "conf=prod"
else:
    conf = ""


def is_local(host_name):
    return socket.gethostname() == host_name


def restart(host_name):
    if is_local(host_name):
        os.system("cd {};sudo ./restart_web.sh {}".format(base_dir, conf))
    else:
        os.system('ssh {} "cd {}; sudo ./restart_web.sh {}"'.format(host_name, base_dir, conf))


def auto_train(business_id, supplier_id):
    write_qa_data(business_id, supplier_id)
    qa_train(business_id, supplier_id)


def copy_model_file(host_name, btype):
    if not is_local(host_name):
        print("start copy_model_file to {}".format(host_name))
        qa_file = qa_file_path.format(btype)
        checkpoint_file = get_last_checkpoint_dir(project_dir, result_dir, btype=btype)
        checkpoint_dir = checkpoint_file[0:checkpoint_file.index("/checkpoints")]
        os.system('ssh {} "mkdir -p {}/checkpoints"'.format(host_name, checkpoint_dir))
        os.system("scp {}/checkpoints/* {}:{}/checkpoints/".format(checkpoint_dir, host_name, checkpoint_dir))
        os.system("scp {}/vocabulary.data {}:{}/vocabulary.data".format(checkpoint_dir, host_name, checkpoint_dir))
        os.system("scp {}/vocabulary.data {}:{}/vocabulary.data".format(checkpoint_dir, host_name, checkpoint_dir))
        os.system("scp {} {}:{}".format(qa_file, host_name, qa_file))
        print("end copy_model_file to {}".format(host_name))


def delete_days_train_file(app_dir, host_name, days=3):
    """
    it is a large risk for delete file, so the method given the fixed path
    """
    dir_path = "{}/apps/{}/runs/".format(base_dir, app_dir)
    if is_local(host_name):
        cmd = "find {} -maxdepth 1 -type d  -mtime +{} -not -path {}".format(dir_path, days, dir_path)
        cmd += " -exec rm -rf {} \;"
    else:
        cmd = "ssh {} ".format(host_name)
        cmd += '" find {} -maxdepth 1 -type d  -mtime +{} -not -path {}'.format(dir_path, days, dir_path)
        cmd += ' -exec rm -rf {} \;"'
    os.system(cmd)
    print("delete host={}, days={} train_file file={}".format(host_name, days, cmd))


if __name__ == '__main__':
    bs_list = SupplierQaData.select_btype()
    auto_train(business_id=0, supplier_id=0)
    if bs_list:
        for business_id, supplier_id in bs_list:
            auto_train(business_id, supplier_id)
    for host_name in hosts:
        if not is_local(host_name):
            for business_id, supplier_id in bs_list:
                btype = "{}_{}".format(business_id, supplier_id)
                copy_model_file(host_name, btype)
        else:
            restart(host_name)
            delete_days_train_file(app_dir, host_name, days=3)
