from tqdm import tqdm
from elasticsearch import Elasticsearch
import xml.dom.minidom as xmldom
import os
import json
import pandas as pd

def fusion_model():

    querys, questions, narratives = generate_query_sets()

    weight1 = 70
    weight2 = 100
    weight3 = 3

    for i in range(len(querys)):

        total_doc = {}

        cur_query = querys[i]

        search_query2 = {"query": {"multi_match" : {"query" : extract_stemming_porter(cur_query), "fields" : ["title", "abstract"]}}, "size" : 5000}
        search_query3 = {"query": {"multi_match" : {"query" : extract_stemming_snowball(cur_query), "fields" : ["title", "abstract"]}}, "size" : 5000}

        query_res_1 = es.search(index="id_meta_gs_stem2_dfr", doc_type="meta_id_stem3", body=search_query2)
        for candidate_doc in query_res_1["hits"]["hits"]:
            total_doc[candidate_doc["_source"]["id"]] = [candidate_doc["_score"]]
            #print(i + 1, "Q0", candidate_doc["_source"]["id"], 0 ,candidate_doc["_score"], "STANDARD")

        query_res_2 = es.search(index="id_meta_gs_stem3_dfr1", doc_type="meta_id_stem3", body=search_query3)
        for candidate_doc in query_res_2["hits"]["hits"]:
            if candidate_doc["_source"]["id"] in total_doc.keys():
                total_doc[candidate_doc["_source"]["id"]].append(candidate_doc["_score"])
            else:
                total_doc[candidate_doc["_source"]["id"]] = [0, candidate_doc["_score"]]
        
        for doc in total_doc:
            if(len(total_doc[doc]) == 1):
                total_doc[doc].append(0)


        query_res_3 = es.search(index="id_meta_gs_stem3_dfr2", doc_type="meta_id_stem3", body=search_query3)
        for candidate_doc in query_res_3["hits"]["hits"]:
            if candidate_doc["_source"]["id"] in total_doc.keys():
                total_doc[candidate_doc["_source"]["id"]].append(candidate_doc["_score"])
            else:
                total_doc[candidate_doc["_source"]["id"]] = [0, 0, candidate_doc["_score"]]

        for doc in total_doc:
            if(len(total_doc[doc]) == 2):
                total_doc[doc].append(0)

        for doc in total_doc:
            weight_sum = 0
            final_score = 0
            if total_doc[doc][0] != 0:
                weight_sum += weight1
                final_score += weight1 * total_doc[doc][0]
            if total_doc[doc][1] != 0:
                weight_sum += weight2
                final_score += weight2 * total_doc[doc][1]
            if total_doc[doc][2] != 0:
                weight_sum += weight3
                final_score += weight3 * total_doc[doc][2]

            final_score /= weight_sum

            print(i + 1, "Q0", doc, 0 ,final_score, "STANDARD")
            
    return

def run_search(cur_query, cur_index, cur_doctype):

    es = Elasticsearch()
    es.indices.create(index='pdf_doc', ignore=400)

    querys, questions, narratives = generate_query_sets()

    for i in range(len(querys)):
        cur_query = querys[i]

        query = {"query": {"multi_match" : {"query" : cur_query, "fields" : ["title", "abstract"]}}}

        cur_query = query
        
        query_res = es.search(index=cur_index, doc_type=cur_doctype, body=cur_query)
    
        for candidate_doc in query_res["hits"]["hits"]:
            print(i + 1, "Q0", candidate_doc["_source"]["id"], 0 ,candidate_doc["_score"], "STANDARD")
        

