from tqdm import tqdm
from elasticsearch import Elasticsearch
import xml.dom.minidom as xmldom
import os
import json
import pandas as pd

def generate_query_sets():

    query_collection = []
    question_collection = []
    narrative_collection = []

    query_datadir = '..//'

    query_datapath = os.path.join(query_datadir, 'topics-rnd5.xml')

    with open(query_datapath, 'r') as topicfile:
        topicfile = xmldom.parse(topicfile)
        elementobj = topicfile.documentElement
        querys = elementobj.getElementsByTagName("query")
        for i in range(len(querys)):
            query_collection.append(querys[i].firstChild.data)
        
        questions = elementobj.getElementsByTagName("question")
        for i in range(len(questions)):
            question_collection.append(questions[i].firstChild.data)
        
        narratives = elementobj.getElementsByTagName("narrative")
        for i in range(len(narratives)):
            narrative_collection.append(narratives[i].firstChild.data)

    return query_collection, question_collection, narrative_collection

def prepare_id_metadata():


    datadir = '..//2020-07-16//'

    datapath = os.path.join(datadir, 'metadata.csv')

    metadata = pd.read_csv(datapath)

    '''if os.path.exists('pdf.json'):
        os.remove('pdf.json')'''
    

    no_pdf = 0
    no_pmc = 0
    no_meta = 0

    uuid = []

    for idx, cur_record in tqdm(metadata.iterrows()):

        cord_uid = cur_record["cord_uid"]
        if cord_uid in uuid:
            continue
        else:
            uuid.append(cord_uid)
        pdf_json_files = cur_record["pdf_json_files"]
        pmc_json_files = cur_record["pmc_json_files"]
        title = cur_record["title"]
        abstract = cur_record["abstract"]

        if idx % 5000 == 0:
            new_file = os.path.join(datadir, "meta_part_lower", str(idx / 5000) + ".json")

        
        with open(new_file, 'a') as meta_collection:
            cur_str = { "index" : { "_index" : "id_meta_lower", "_type" : "meta_id_lower", "_id" : str(idx) } }
            #print(cur_str)
            json.dump(cur_str, meta_collection)
            meta_collection.write("\n")

            id_meta = {"id" : str(cord_uid), "title" : to_lower(title), "abstract" : to_lower(abstract)}
            json.dump(id_meta, meta_collection)
            meta_collection.write("\n")

        
        with open(new_file, 'a') as pmc_collection:
            cur_str = { "index" : { "_index" : "id_pmc", "_type" : "pmc_id", "_id" : str(idx) } }
            #print(cur_str)
            json.dump(cur_str, pmc_collection)
            pmc_collection.write("\n")

            id_pmc = {"id" : str(cord_uid)}
            try:
                pmc_json_files = pmc_json_files.split(',')
                pmc_json_files = pmc_json_files[0]
                pmc_pathpath = os.path.join(datadir, pmc_json_files)
                with open(pmc_pathpath, 'r') as pmcnow:
                    cur_data = json.load(pmcnow)
                    id_pmc.update({"metadata" : cur_data["metadata"]})
                    id_pmc.update({"body_text" : cur_data["body_text"]})
            except:
                no_pmc += 1
            json.dump(id_pmc, pmc_collection)
            pmc_collection.write("\n")
            
        
        with open(new_file, 'a') as pdf_collection:
            cur_str = { "index" : { "_index" : "id_pdf", "_type" : "pdf_id", "_id" : str(idx) } }
            #print(cur_str)
            json.dump(cur_str, pdf_collection)
            pdf_collection.write("\n")

            id_pdf = {"id" : str(cord_uid)}
            try:
                pdf_json_files = pdf_json_files.split(',')
                pdf_json_files = pdf_json_files[0]
                pdf_pathpath = os.path.join(datadir, pdf_json_files)
                with open(pdf_pathpath, 'r') as pdfnow:
                    cur_data = json.load(pdfnow)
                    id_pdf.update({"metadata" : cur_data["metadata"]})
                    id_pdf.update({"abstract" : cur_data["abstract"]})
                    id_pdf.update({"body_text" : cur_data["body_text"]})
            except:
                no_pdf += 1
            json.dump(id_pdf, pdf_collection)
            pdf_collection.write("\n")

    return

def modify_qrel():

    datapath = "..//qrels-covid_d5_j0.5-5.txt"

    origin = open(datapath, 'r')

    with open('new_qrel.txt', 'w') as qrel:
        for line in origin:
            topicid, roundid, docid, rel = line.split(' ')
            if rel == "2\n":
                rel = "1\n"
            qrel.write(topicid + " " + roundid + " " + docid + " " + rel)

    return
