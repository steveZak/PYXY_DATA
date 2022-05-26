import os, re
import numpy as np
import json
#import param_extraction_utils as parext    #for later
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'\w+')


def generateSynonyms(model, criteria):
    # gathering synonyms via wordnet to sub for criteria: for now just blindly getting all word senses
    criteria_syns = {}
    for c in criteria:
        print(c)
        stop_words = set(stopwords.words('english'))
        synsets = model.most_similar(positive=c, topn=50)  # 150/50
        nearest_neighbours = dict()
        for w in c:
            nearest_neighbours[w] = 1.0
        for syn in synsets:
            if syn[0] not in stop_words:
                nearest_neighbours[syn[0]] = syn[1]
        criteria_syns[c[0]] = nearest_neighbours
    with open("mood_word_pool.json", 'w') as file:  # parameter/moods
        json.dump(criteria_syns, file)
    return criteria_syns


def extract_embeddings(reviews):
    #stub method for later
    return []


#removes stopwords from tokenized review text
def remove_stopwords_lemm(text_arr):
    output = []
    stop_words = set(stopwords.words('english'))
    for word in text_arr:
        if word not in stop_words:
            output.append(lemmatizer.lemmatize(word))
    return output


def tf_idf(reviews, criteria, param_type):
    if param_type == 'mood':
        with open("mood_word_pool.json", 'r') as file:
            criteria_syns = json.load(file)
    else:
        with open("parameter_word_pool.json", 'r') as file:
            criteria_syns = json.load(file)
    #cleaning up the reviews to create the review text
    for r in reviews.keys():
        reviews[r] = remove_stopwords_lemm(tokenizer.tokenize(reviews[r]))

    # #gathering synonyms via wordnet to sub for criteria: for now just blindly getting all word senses
    # criteria_syns = {}
    # for c in criteria:
    #     synsets = model.most_similar(positive=c, topn=200)
    #     nearest_neighbours = dict()
    #     for w in c[0]:
    #         nearest_neighbours[w] = 1.0
    #     for syn in synsets:
    #         nearest_neighbours[syn[0]] = syn[1]
    #     criteria_syns[c[0]] = nearest_neighbours

    # initializing the dict for docfreqs and termfreqs
    docfreq = {}
    termfreq = {}
    for c in criteria:
        docfreq[c[0]] = 0
        for r in reviews.keys():
            termfreq[(c[0], r)] = 0

    # getting docfreqs (boolean)
    for r in reviews.keys():
        for c in criteria:
            # termfreq[(c, r)] = reviews[r].count(c) / len(reviews[r])
            if termfreq[(c[0], r)] > 0:
                docfreq[c[0]] = 1
            for synonym in criteria_syns[c[0]].keys():
                termfreq[(c[0], r)] += reviews[r].count(synonym)*criteria_syns[c[0]].get(synonym) / len(reviews[r])

    # actually smoothing
    #idf_smooth = {(np.log(len(reviews.keys())) - np.log(docfreq[c] + 1) + 1) for c in criteria}
    idf_smooth = {}
    for c in criteria:
        idf_smooth[c[0]] = (np.log(len(reviews.keys())) - np.log(docfreq[c[0]] + 1) + 1)
    #tf_idf_params = {termfreq[(c, r)]*idf_smooth[c] for c in criteria for r in reviews.keys()}
    tf_idf_params = {}
    for r in reviews.keys():
        outdict = {}
        max_c = 0
        for c in criteria:
            outdict[c[0]] = termfreq[(c[0], r)]*idf_smooth[c[0]]
            max_c = outdict[c[0]] if outdict[c[0]] > max_c else max_c
        tf_idf_params[r] = outdict

    return tf_idf_params


def loadTextData(city_dir):
    corpus = dict()
    with open("CITY_DATABASES/" + city_dir + "/text.json", 'r') as file:
        data = json.load(file)['sights']
        for sight in data:
            trip = sight['text']['trip'] if 'trip' in data[0]['text'] else ""
            google = sight['text']['google'] if 'google' in data[0]['text'] else sight['reviews']['google']
            # website = [elt['content'] for elt in sight['text']['website']] if len(sight['text']['website']) else []
            corpus[sight['place_id']] = " ".join([sight['text']['quote'],
                                                  sight['text']['wiki'],
                                                  sight['text']['brit'],
                                                  sight['text']['tags'].replace('_', ' '),
                                                  " ".join(trip),
                                                  " ".join(google)])  # " ".join(website)
    return corpus
