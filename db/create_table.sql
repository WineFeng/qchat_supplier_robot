
-- robot_default_config 管理后台默认问题列表设置
create table supplier_robot_config(
  id serial primary key ,
  business_id int not null,
  supplier_id int not null,
	default_questions varchar(1000)[],
	create_time timestamptz default now(),
	update_time timestamptz default now(),
	update_user varchar(64),
	status int default 1

);
CREATE UNIQUE INDEX supplier_robot_config_id_uindex ON supplier_robot_config (id);
CREATE UNIQUE INDEX supplier_robot_config_business_id_supplier_id_index on supplier_robot_config using btree (business_id, supplier_id)
CREATE INDEX supplier_robot_config_id_create_time_index ON supplier_robot_config (id,create_time);

COMMENT ON TABLE public.supplier_robot_config IS '管理后台默认问题列表设置';
COMMENT ON COLUMN public.supplier_robot_config.id IS '自增id';
COMMENT ON COLUMN public.supplier_robot_config.business_id IS '业务线ID';
COMMENT ON COLUMN public.supplier_robot_config.supplier_id IS '店铺ID';
COMMENT ON COLUMN public.supplier_robot_config.default_questions IS '默认问题列表';
COMMENT ON COLUMN public.supplier_robot_config.create_time IS '创建时间';
COMMENT ON COLUMN public.supplier_robot_config.update_time IS '操作时间';
COMMENT ON COLUMN public.supplier_robot_config.update_user IS '操作者';
COMMENT ON COLUMN public.supplier_robot_config.status IS '状态标志';

insert into supplier_robot_config(business_id, supplier_id,default_questions, update_user,status) values (0,0,'{你好,你是谁}','',1);

-- robot_qa_data 管理后台问题集设置表
create table supplier_qa_data(
  id serial primary key ,
  business_id int not null,
  supplier_id int not null,
	question varchar(200)[] not null,
	answer varchar(65536) not null,
	create_time timestamptz default now(),
	update_time timestamptz default now(),
	update_user varchar(64),
	status int default 1

);
CREATE UNIQUE INDEX supplier_qa_data_id_uindex ON supplier_qa_data (id);
CREATE INDEX supplier_qa_data_business_id_supplier_id_index on supplier_qa_data using btree (business_id, supplier_id)
CREATE INDEX supplier_qa_data_id_create_time_index ON supplier_qa_data (id,create_time);

COMMENT ON TABLE public.supplier_qa_data IS '管理后台问题集设置表';
COMMENT ON COLUMN public.supplier_qa_data.id IS '自增id';
COMMENT ON COLUMN public.supplier_qa_data.business_id IS '业务线ID';
COMMENT ON COLUMN public.supplier_qa_data.supplier_id IS '店铺ID';
COMMENT ON COLUMN public.supplier_qa_data.question IS '设置的问题';
COMMENT ON COLUMN public.supplier_qa_data.answer IS '问题对应的答案';
COMMENT ON COLUMN public.supplier_qa_data.create_time IS '创建时间';
COMMENT ON COLUMN public.supplier_qa_data.update_time IS '操作时间';
COMMENT ON COLUMN public.supplier_qa_data.update_user IS '操作者';
COMMENT ON COLUMN public.supplier_qa_data.status IS '状态标志';

insert into supplier_qa_data(business_id, supplier_id,question,answer, update_user,status) values (0,0,'{你好,你好啊,在吗}','您好,很高兴为您服务~','',1);
insert into supplier_qa_data(business_id, supplier_id,question,answer, update_user,status) values (0,0,'{你是谁,你叫什么名字,你叫什么}','您好,机器人小星~','',1);

-- robot_chat_history用户对话反馈表
create table  supplier_qa_history
(
    id  serial  primary key,
    create_time timestamptz default now() ,
    question varchar(500) not null,
    answer varchar(1000) not null,
    origin_question varchar(500) not null,
    qtype bigint ,
    btype varchar(200),
    username varchar(64),
    business_id int not null,
    supplier_id bigint not null,
    intent_type int default 0,
    classify varchar(20),
    is_worked  varchar(2) default null,
    right_count int default 0,
    wrong_count int default 0,
    status int default 0,
    update_time timestamptz default now() ,
    update_user varchar(64),
    robot varchar(64),
    qa_dict varchar(65535)
);
CREATE UNIQUE INDEX supplier_qa_history_id_uindex ON supplier_qa_history (id);
CREATE INDEX supplier_qa_history_create_time_index ON supplier_qa_history (create_time);
CREATE INDEX supplier_qa_history_business_id_supplier_id_index ON supplier_qa_history using btree (business_id, supplier_id);
CREATE INDEX supplier_qa_history_create_time_index ON supplier_qa_history (create_time);
CREATE INDEX supplier_qa_history_robot_index ON supplier_qa_history (robot);

COMMENT ON TABLE public.supplier_qa_history IS '用户对话反馈表';
COMMENT ON COLUMN public.supplier_qa_history.id IS '自增id';
COMMENT ON COLUMN public.supplier_qa_history.create_time IS '对话建立时间';
COMMENT ON COLUMN public.supplier_qa_history.question IS '用户问题';
COMMENT ON COLUMN public.supplier_qa_history.answer IS '匹配用户问题答案';
COMMENT ON COLUMN public.supplier_qa_history.origin_question IS '匹配的标准问题';
COMMENT ON COLUMN public.supplier_qa_history.qtype IS '匹配问题的类型';
COMMENT ON COLUMN public.supplier_qa_history.btype IS 'btype';
COMMENT ON COLUMN public.supplier_qa_history.username IS '用户id';
COMMENT ON COLUMN public.supplier_qa_history.business_id IS '业务线ID';
COMMENT ON COLUMN public.supplier_qa_history.supplier_id IS '店铺id';
COMMENT ON COLUMN public.supplier_qa_history.intent_type IS '用户问题意图分类';
COMMENT ON COLUMN public.supplier_qa_history.classify IS '用户问题分类';
COMMENT ON COLUMN public.supplier_qa_history.is_worked IS '答案是否正确的反馈,0否,1是';
COMMENT ON COLUMN public.supplier_qa_history.right_count IS '反馈"是"的次数';
COMMENT ON COLUMN public.supplier_qa_history.wrong_count IS '反馈"否"的次数';
COMMENT ON COLUMN public.supplier_qa_history.status IS '商家处理状态,0未处理,1已处理';
COMMENT ON COLUMN public.supplier_qa_history.update_time IS '操作更新时间';
COMMENT ON COLUMN public.supplier_qa_history.update_user IS '商家后台数据的操作者';
COMMENT ON COLUMN public.supplier_qa_history.robot IS '机器人id';
COMMENT ON COLUMN public.supplier_qa_history.qa_dict IS '所有的数据信息';
