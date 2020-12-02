from tqdm import tqdm
from elasticsearch import Elasticsearch
import xml.dom.minidom as xmldom
import os
import json
import pandas as pd
import jsonargparse

from nltk.stem.porter import PorterStemmer  
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer 

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

def delete_stopwords(text):

    if type(text) is not str:
        return text

    en_stops = ['very', 'ourselves', 'am', 'doesn', 'through', 'me', 'against', 'up', 'just', 'her', 'ours', 'couldn', 'because', 'is', 'isn', 'it', 'only', 'in', 'such', 'too', 'mustn', 'under', 'their', 'if', 'to', 'my', 'himself', 'after', 'why', 'while', 'can', 'each', 'itself', 'his', 'all', 'once', 'herself', 'more', 'our', 'they', 'hasn', 'on', 'ma', 'them', 'its', 'where', 'did', 'll', 'you', 'didn', 'nor', 'as', 'now', 'before', 'those', 'yours', 'from', 'who', 'was', 'm', 'been', 'will', 'into', 'same', 'how', 'some', 'of', 'out', 'with', 's', 'being', 't', 'mightn', 'she', 'again', 'be', 'by', 'shan', 'have', 'yourselves', 'needn', 'and', 'are', 'o', 'these', 'further', 'most', 'yourself', 'having', 'aren', 'here', 'he', 'were', 'but', 'this', 'myself', 'own', 'we', 'so', 'i', 'does', 'both', 'when', 'between', 'd', 'had', 'the', 'y', 'has', 'down', 'off', 'than', 'haven', 'whom', 'wouldn', 'should', 've', 'over', 'themselves', 'few', 'then', 'hadn', 'what', 'until', 'won', 'no', 'about', 'any', 'that', 'for', 'shouldn', 'don', 'do', 'there', 'doing', 'an', 'or', 'ain', 'hers', 'wasn', 'weren', 'above', 'a', 'at', 'your', 'theirs', 'below', 'other', 'not', 're', 'him', 'during', 'which']

    text = text.split(' ')
    new_text = []

    for word in text:
        if word.lower() not in en_stops:
            new_text.append(word)
    
    new_text = ' '.join(new_text)

    return new_text

def extract_stemming_porter(text):

    if type(text) is not str:
        return text

    porter_stemmer = PorterStemmer()

    text = text.split(' ')
    new_text = []
    for word in text:
        new_text.append(porter_stemmer.stem(word))
    
    new_text = ' '.join(new_text)

    return new_text

def extract_stemming_lancaster(text):

    if type(text) is not str:
        return text

    lancaster_stemmer = LancasterStemmer()

    text = text.split(' ')
    new_text = []
    for word in text:
        new_text.append(lancaster_stemmer.stem(word))
    
    new_text = ' '.join(new_text)

    return new_text

def extract_stemming_snowball(text):

    if type(text) is not str:
        return text

    snowball_stemmer = SnowballStemmer("english")  

    text = text.split(' ')
    new_text = []
    for word in text:
        new_text.append(snowball_stemmer.stem(word))
    
    new_text = ' '.join(new_text)

    return new_text

if __name__ == "__main__":

    parser = jsonargparse.ArgumentParser(description="index")
    parser.add_argument('-i', '--index3', type=str)
    parser.add_argument('--doc_type3', type=str)

    opt = parser.parse_args()

    # # print(opt.index3)
    if os.path.exists("res.txt"):
        os.remove("res.txt")


    es = Elasticsearch()

    querys, questions, narratives = generate_query_sets()

    print(f"\n\nopt.doc_type3: {opt.doc_type3}")
    with open('res.txt', 'w+') as f:
        for i in tqdm(range(len(querys))):

            if opt.doc_type3 == "meta_id_stop":
                cur_query = delete_stopwords( querys[i] )
            elif opt.doc_type3 == "meta_id_stem":
                cur_query = extract_stemming_lancaster( querys[i] )
            elif opt.doc_type3 == "meta_id_stem2":
                cur_query = extract_stemming_porter( querys[i] )
            elif opt.doc_type3 == "meta_id_stem3":
                cur_query = extract_stemming_snowball( querys[i] ) 
            else:
                cur_query = querys[i]
            
            # index3 = "id_meta"
            index3 = opt.index3
            # doc_type3 = "meta_id"
            doc_type3 = opt.doc_type3

            query = {
                        "query": 
                        {
                            "multi_match" : 
                            {
                                "query" : cur_query, 
                                "fields" : ["title", "abstract"]
                            }
                        }, 
                        "size" : 5000
                    }

            cur_query = query
            cur_index = index3
            cur_doctype = doc_type3
            query_res = es.search(index=cur_index, doc_type=cur_doctype, body=cur_query)
            
            for candidate_doc in query_res["hits"]["hits"]:
                res = str(i + 1) + " Q0 " + candidate_doc["_source"]["id"] + " 0 " + str(candidate_doc["_score"]) + " STANDARD\n"
                f.write(res)