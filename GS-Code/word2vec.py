import io
import os
import time
import numpy as np
import fasttext
import pandas as pd
import nltk
from gensim.models import FastText
from gensim import utils
from gensim.utils import tokenize
from gensim.test.utils import datapath
from tqdm import tqdm

import xml.dom.minidom as xmldom
import json
import jsonargparse

from nltk.stem.porter import PorterStemmer  
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer 

def load_vectors(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = map(float, tokens[1:])
    return data

def Get_meta_data():

    datadir = '..//2020-07-16//'

    datapath = os.path.join(datadir, 'metadata.csv')

    metadata = pd.read_csv(datapath)

    meta_data = []
    uuid = []

    for idx, cur_record in metadata.iterrows():

        cord_uid = cur_record["cord_uid"]
        if cord_uid in uuid:
            continue
        else:
            uuid.append(cord_uid)
        title = cur_record["title"]
        abstract = cur_record["abstract"]
        
        cur_doc = {cord_uid : [title, abstract]}

        meta_data.append(cur_doc)

    return meta_data

def Prepare_fast_meta_data():
    start_t = time.time()
    meta_data_list = Get_meta_data()
    end_t = time.time()
    print("Load meta_data Succeed! time: {:.2f}s".format(end_t - start_t))        # 729s
    
    num = 0
    with open('meta_data.txt', 'w+') as f:
        for meta_data in meta_data_list:
            for key,value in meta_data.items():
                if type(value[0]) != str:
                    value[0] = str(value[0])
                if type(value[1]) != str:
                    value[1] = str(value[1])

                line = key + "-$**$-" + value[0] + "-$**$-" + value[1]
                f.write(line+"\n")

                num += 1
                print(num)

def Fast_read_meta_data():

    uuid_list, title_list, abstract_list = [], [], []
    with open('meta_data.txt', 'r') as f:
        for line in f:
            line_split = line.split("-$**$-")

            uuid = line_split[0]
            title = line_split[1]
            abstract = line_split[2]

            uuid_list.append(uuid)
            title_list.append(title)
            abstract_list.append(abstract)
    
    return uuid_list, title_list, abstract_list

def GS_tokenize(string):
    return [x for x in tokenize(string)]

def Calculate_mean_embedding_vector(model, token_list):

    if len(token_list) == 0:
        mean_vector = np.zeros(( 300 ))
    else:
        all_token_vector = np.zeros(( len(token_list), 300 ))
        for i, token in enumerate(token_list):
            vector = model.wv[token]
            all_token_vector[i] = vector
        mean_vector = np.mean(all_token_vector,axis=0)
    # print(np.shape(mean_vector))

    return mean_vector

def Cosine_distance(vector1, vector2):
    """
    Calculate Cosine_distance between vector1 & vector2
    """
    a = np.dot(vector1,vector2)
    b = (np.linalg.norm(vector1)*(np.linalg.norm(vector2)))
    
    if b == 0:
        return 0
    else:
        return a / b

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

if __name__ == "__main__":

    # start_t = time.time()
    # w2v_data = load_vectors("wiki-news-300d-1M-subword.vec")
    # end_t = time.time()
    # print("Load Fasttext model Succeed! time: {:.2f}s".format(end_t - start_t))

    # with open('word2vec_res.txt', 'w+') as f:
    #     num = 0
    #     for key,value in w2v_data.items():
    #         # # line = key + " " + str(np.shape(value)) + "\n"
    #         vector = np.array(list(value))
    #         line = key + " " + str(np.shape(vector)) + "\n"
    #         f.write(key+"\n")
    #         print(key, np.shape(vector))
    #         num += 1

    #         if num == 10:
    #             break

    '''
        1. load model
    '''
    start_t = time.time()

    FASTTEXTFILE = "wiki-news-300d-1M-subword.bin"
    model = FastText.load_fasttext_format(FASTTEXTFILE)
    # FASTTEXTFILE = datapath("wiki-news-300d-1M-subword.bin")
    # model = load_facebook_model(FASTTEXTFILE)

    end_t = time.time()
    print("Load Fasttext model Succeed! time: {:.2f}s".format(end_t - start_t))           # 228s

    # print(model.wv['covid-19'])                   # dim=300
    # print(np.shape(model.wv['covid-19']))

    # # model.build_vocab(new_sentences, update=True)  # Update the vocabulary
    # # model.train(new_sentences, total_examples=len(new_sentences), epochs=model.epochs)

    '''
        2. load data & tokenize & prepare embedding vector
    '''
    uuid_list, title_list, abstract_list = Fast_read_meta_data()                # 191175 passages
    print(len(uuid_list))

    vector_title_list = []
    vector_abstract_list = []

    for i in tqdm(range(len(uuid_list))):
        title = title_list[i]
        abstract = abstract_list[i]

        token_list = GS_tokenize(title)
        title_mean_vector = Calculate_mean_embedding_vector(model, token_list)

        token_list = GS_tokenize(abstract)
        abstract_mean_vector = Calculate_mean_embedding_vector(model, token_list)

        vector_title_list.append(title_mean_vector)
        vector_abstract_list.append(abstract_mean_vector)

        # print(f"passage {i} succeed! {np.shape(title_mean_vector)}")            # (300,)

    '''
        3. load query data & get simi_score & write txt
    '''
    querys, questions, narratives = generate_query_sets()
        
    if os.path.exists("res.txt"):
        os.remove("res.txt")
    with open('res.txt', 'w+') as f:
        for i in tqdm(range(len(querys))):
            cur_query = querys[i]
            token_list = GS_tokenize(cur_query)
            query_vector = Calculate_mean_embedding_vector(model, token_list)

            simi_list = []
            for index_find in range(len(uuid_list)):
                title_vector = vector_title_list[index_find]
                abstract_vector = vector_abstract_list[index_find]

                title_simi = Cosine_distance(query_vector, title_vector)
                ab_simi = Cosine_distance(query_vector, abstract_vector)

                final_simi = title_simi + ab_simi
                simi_list.append(final_simi)
            k_max_simi_index_list = np.array(simi_list).argsort()[-5000:][::-1]

            for res_index in k_max_simi_index_list:
                    res = str(i + 1) + " Q0 " + uuid_list[res_index] + " 0 " + str(simi_list[res_index]) + " STANDARD\n"
                    f.write(res)

    

   

