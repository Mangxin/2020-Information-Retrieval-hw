import os
from nltk.stem.porter import PorterStemmer  
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer 
import pandas as pd
import tqdm

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

def to_lower(text):

    if type(text) is not str:
        return text

    text = text.split(' ')
    new_text = []

    for word in text:
        new_text.append(word.lower())
    
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

def meta_data():

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
