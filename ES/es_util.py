#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys

sys.path.append('././')
from get_config import get_config_file
import random
from elasticsearch import Elasticsearch

config = get_config_file()


class EsUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_es_servers():
        SAAS = (config["elasticsearch"]["SAAS1"], config["elasticsearch"]["SAAS2"], config["elasticsearch"]["SAAS3"])
        rand = random.randint(0, 2)
        url = SAAS[rand]
        print(url)
        es_client = Elasticsearch(url)
        return es_client

    @staticmethod
    def create_es_index(business_id, supplier_id):
        es_client = EsUtil.get_es_servers()
        es_index = 'q_supplier_robot_{}_{}'.format(business_id, supplier_id)
        if not es_client.indices.exists(index=es_index):
            es_client.indices.create(index=es_index, body={}, ignore=[400, 404])
        return es_index, es_client

    @staticmethod
    def es_similar_question(business_id, supplier_id, question):
        es_index, es_client = EsUtil.create_es_index(business_id, supplier_id)
        similar_list = []
        res = es_client.search(index=es_index,
                               body={"query": {"bool": {
                                   "must": [{"term": {"business_id": business_id}},
                                            {"term": {"supplier_id": supplier_id}},
                                            {"match": {"question": question}}
                                            ]
                               }}})
        total = res['hits']['total']
        hits = res['hits']['hits']
        if total < 5:
            for hit in hits:
                similar_list.append(hit["_source"])
        else:
            for i in range(5):
                similar_list.append(hits[i]["_source"])
        print(similar_list)
        return similar_list


if __name__ == '__main__':
    esutil = EsUtil.es_similar_question(1, 1, '问题')
