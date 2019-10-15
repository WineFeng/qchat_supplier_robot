## 环境
###　Linux安装python3.6
#### 1.安装依赖环境
```
  $ yum install gcc
  $ yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
```
#### 2.下载Python3
```
  $ wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
```
#### 3.安装python3
```
  $ tar -zxvf Python-3.6.1.tgz
  # cd Python-3.6.1
  # mkdir -p /usr/local/python3
  # ./configure --prefix=/usr/local/python3
  # make
  # make install
```
#### 4.建立python3的软链
```
  # ln -s /usr/local/python3/bin/python3 /usr/bin/python3
```
#### 5.并将/usr/local/python3/bin加入PATH
```
  # vim ~/.bash_profile
    PATH=$PATH:$HOME/bin:/usr/local/python3/bin
  # source ~/.bash_profile
```
#### 6.检查Python3及pip3是否正常可用
```
  # python3 -V
  # pip3 -V
```
#### 7.安装虚拟环境
```
  # pip3 install virtualenv
  # virtualenv venv 
```
### 安装python依赖包
```
  # source ./venv/bin/activate
  # pip3 install -r requirements.txt
```

## 启动服务
```
# python3 run.py
  包括训练模型和启动机器人服务
或者:
1.训练
  有一些基本的聊天数据在service/robot/data/qa_0_0.txt中
  后台管理页面自己添加的数据集会以qa_{}_{}.txt的模式保存
  #  python3 service/robot/train.py
  
2.测试
  #  python3 service/robot/test.py
3.启动机器人服务
   测试环境:
  # ./restart_web.sh 
  线上环境:
  # ./restart_web.sh  conf=prod
```

### 服务配置信息
```
   ./conf目录下
   1.conf.ini 基本信息文件配置
     postgresql:数据库连接信息配置
     qchat:发消息的接口和客户端点击反馈的url
     hosts:服务启动的所在的机器host
     elasticsearch:es搜索连接信息
   2.logging.ini服务日志文件配置 
     loggers:日志名称,根据自己所需添加相应的日志
   3.uwsgi_dl.ini web服务配置信息
     module:需要启动的web服务
```

### 数据集
```
  1.默认闲聊数据集合:service/robot/data/qa_0_0.txt
  2.自定义数据集(需要在后台管理系统添加,可以不添加)
  建表语句:db/create_table.sql
  (1).机器人默认问题列表,设置常规需要解决用户的问题,在用户咨询的时候展示:
     supplier_robot_config
  (2).自定义问题集,店铺可以设置自己的数据集,单独训练店铺模型
     supplier_qa_data
  (3).用户咨询反馈表,可以搜集用户咨询的问题和机器人的答案,修正处理答案之后再添加到数据集里面去
     supplier_qa_history

```

## 启动服务
```
# python3 run.py
  包括训练模型和启动机器人服务
或者:
1.训练:默认聊天数据+自定义数据集
  默认聊天数据:service/robot/data/qa_0_0.txt
  自定义数据集会:以"qa_{}_{}.txt".format(business_id,supplier_id)的模式保存
  # python3 service/robot/train_qa.py
  
2.测试
  # python3 service/robot/test_qa.py
3.启动机器人服务
   测试环境:
  # ./restart_web.sh 
  线上环境:
  # ./restart_web.sh  conf=prod
```
