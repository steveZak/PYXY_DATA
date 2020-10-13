import analyze_utils as au
import re
import os
import json
import numpy as np
# from loadModel import load

# walking areas, markets, specific neighbourhoods, lakes, beaches, water, embankment?
# attach tags, (Museum, Park, Nightclub, etc.)
# search for more specific tags (i.e. parks in NYC)
# implement nearby search to cover all spots
# (screen for tags, give option to users to flag it?)
# include the functionality to see sights around you

criteria = [["amusement", "entertainment"],
            ["animals", "zoo", "creatures"],
            ["architecture", "building"],
            ["art", "painting", "sculpture", "graffiti", "gallery"],
            ["beach", "coast", "swimming"],
            ["books", "literature", "library", "education"],
            ["cosmopolitan", "international", "world", "country", "race"],
            ["culture", "heritage", "tradition"],
            ["engineering", "transportation", "plane", "rail", "car"],
            ["family", "children", "group"],
            ["fashion", "clothes"],
            ["food", "snacks", "cafe", "eatery", "restaurant"],
            ["friends", "socialising", "gatherings", "group"],
            ["hiking", "mountains", "climbing", "hill"],
            ["history", "memoir", "past"],
            ["hospitality", "inviting"],
            ["instagram", "aesthetic", "beautiful", "photos", "pictures"],
            ["military", "war", "castle", "armory"],
            ["music", "concert"],
            ["movies", "film"],
            ["nature", "park", "garden", "green"],
            ["nightlife", "party"],
            ["original", "unique", "authenticity", "authentic"],
            ["religion", "temple", "mosque", "church", "prayer"],
            ["science", "physics", "chemistry", "mathematics", "biology"],
            ["shopping", "boutique", "store", "market", "souvenir"],
            ["sport", "stadium", "competition"],
            ["views", "lookout", "observation"],
            ["walking", "outdoors", "open-air"],
            ["water", "sea", "coast", "river", "lake", "ocean", "canal", "navy", "maritime"]]

mood_criteria = [["adventurous", "risky", "brave", "adventuresome"],
                 ["amused", "amusement", "entertaining"],
                 ["calm", "tranquil", "peaceful", "serenity"],
                 ["curious", "interesting", "captivating"],
                 ["dreamy", "magical"],
                 ["exciting", "joyful", "happy"],
                 ["impressive", "awe", "admiration", "powerful"],
                 ["inspiring", "motivating", "energetic"],
                 ["romantic", "charming", "sexy"],
                 ["scary", "horror", "fear"],
                 ["thoughtful", "smart", "wise"],
                 ["touched", "sad", "sorrow", "compassion"]]

# analyse and upload to cloud database


def updateProfiles(city_dir, new_params, param_type):
    with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/profiles.json", 'r') as old_file:
        data = json.load(old_file)
        new_data = {'sights': list()}
        for place_id in new_params.keys():
            params = new_params[place_id]
            for old_sight in data['sights']:
                if place_id == old_sight['place_id']:
                    old_sight[param_type] = list(params.values())
                    new_data['sights'].append(old_sight)
    with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/profiles.json", 'w') as file:
        json.dump(new_data, file, indent=2)


def main(city_dir_name, param):
    # get text data from csv
    sight_corpus = au.loadTextData(city_dir_name)
    review_agg_sight = {}
    # preprocessing
    for sight in sight_corpus.keys():
        agg_text = sight_corpus[sight]
        refined_text = re.sub(r'[^a-zA-Z0-9]+', " ", agg_text)
        review_agg_sight[sight] = refined_text.lower()
    # generate semantic params with preset category vocab lists and tf-idf
    # check if this gets 1 document or n words
    if param == "cat_params":
        params = au.tf_idf(review_agg_sight, criteria, 'cat')
    else:
        params = au.tf_idf(review_agg_sight, mood_criteria, 'mood')
    # generate non-semantic params generated with sentence embeddings
    # noncat_params = au.extract_embeddings(review_agg_sight)
    # save params locally in a separate csv file called params.csv in each city folder
    if param == "mood_params":
        updateProfiles(city_dir_name, params, 'mood_params')
        return
    updateProfiles(city_dir_name, params, 'cat_params')


def generateGlobalVectors():
    global_means = {}
    global_vars = {}
    count = 0
    for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
        for dir in dirs:
            if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir) and isAnalyzeDone(dir):
                with open("CITY_DATABASES/" + dir + '/profiles.json') as file:
                    sights = json.load(file)
                for sight in sights['sights']:
                    count += 1
                    if 'cat' in global_means:
                        global_means['cat'] = [a+b for a, b in zip(sight['cat_params'], global_means['cat'])]
                    else:
                        global_means['cat'] = sight['cat_params']
                    if 'mood' in global_means:
                        global_means['mood'] = [a+b for a, b in zip(sight['mood_params'], global_means['mood'])]
                    else:
                        global_means['mood'] = sight['mood_params']
    global_means['cat'] = [cat/count for cat in global_means['cat']]
    global_means['mood'] = [mood/count for mood in global_means['mood']]
    for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
        for dir in dirs:
            if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir) and isAnalyzeDone(dir):
                with open("CITY_DATABASES/" + dir + '/profiles.json') as file:
                    sights = json.load(file)
                for sight in sights['sights']:
                    if 'cat' in global_vars:
                        global_vars['cat'] = [(a-mean)*(a-mean)+b for a, b, mean in zip(sight['cat_params'], global_vars['cat'], global_means['cat'])]
                    else:
                        global_vars['cat'] = [(a-mean)*(a-mean) for a, mean in zip(sight['cat_params'], global_means['cat'])]
                    if 'mood' in global_vars:
                        global_vars['mood'] = [(a-mean)*(a-mean)+b for a, b, mean in zip(sight['mood_params'], global_vars['mood'], global_means['mood'])]
                    else:
                        global_vars['mood'] = [(a-mean)*(a-mean) for a, mean in zip(sight['mood_params'], global_means['mood'])]
    print("Total of " + str(count) + " sights")
    global_vars['cat'] = [cat/count for cat in global_vars['cat']]
    global_vars['mood'] = [mood/count for mood in global_vars['mood']]
    return global_means, global_vars


def generateNormalisedVectors(global_means, global_vars, city_dir):
    cats_times = [0.75, 1.0, 1.0, 1.0, 1.5, 1.75, 1.25, 1.25, 1.0, 0.75, 1.5, 0.75, 2.0, 1.0, 1.0, 0.75, 1.0, 2.0,
                  1.25, 1.5, 0.75, 1.25, 1.25, 1.0, 0.75, 1.0, 0.5, 0.75, 1.25, 1.0]
    with open("CITY_DATABASES/" + city_dir + '/profiles.json') as file:
        sights = json.load(file)
    for i in range(len(sights['sights'])):
        sights['sights'][i]['global_cat_params'] = [(cat-global_cat_mean)/np.sqrt(global_cat_var) for cat, global_cat_mean, global_cat_var in zip(sights['sights'][i]['cat_params'], global_means['cat'], global_vars['cat'])]
        sights['sights'][i]['global_mood_params'] = [(mood-global_mood_mean)/np.sqrt(global_mood_var) for mood, global_mood_mean, global_mood_var in zip(sights['sights'][i]['mood_params'], global_means['mood'], global_vars['mood'])]
        idxs = np.argsort(sights['sights'][i]['global_cat_params'])[::-1][:4].tolist()
        sights['sights'][i]['top_cats'] = [criteria[idx][0] for idx in idxs]
        duration = sum([cats_times[idx] for idx in idxs])/4
        sights['sights'][i]['duration'] = duration
    with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/profiles.json", 'w') as file:
        json.dump(sights, file, indent=2)


def isMetadataGathered(city_dir):
    if os.path.exists("CITY_DATABASES/" + city_dir + '/text.json'):
        return True
    return False


def isTextMetadataFinal(dir):
    with open("CITY_DATABASES/" + dir + '/text.json') as file:
        data = json.load(file)
    if 'sights' in data:
        return True
    return False


def isTextFinal(dir):
    with open("CITY_DATABASES/" + dir + '/text.json') as file:
        data = json.load(file)
    if 'google' not in data['sights'][0]['text'] or 'trip' not in data['sights'][0]['text']:
        return False
    return True


def isAnalyzeDone(dir):
    with open("CITY_DATABASES/" + dir + '/profiles.json') as file:
        data = json.load(file)['sights']
    if 'mood_params' in data[0]:
        return True
    return False


# model = load("glove.42B.300d.txt")
# au.generateSynonyms(model, criteria)
# au.generateSynonyms(model, mood_criteria)


# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for dir in dirs:
#         if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir):
#             print(dir)
#             main(dir, 'cat_params')
#             main(dir, 'mood_params')

# global_means, global_vars = generateGlobalVectors()  # generate mean and variance
# print(global_means)
# print(global_vars)
# {'cat': [0.1612173849552303, 0.11225464724230765, 0.22464176250980894, 0.23127285890041, 0.3048601826377969, 0.1451288720358379, 0.3982890164164118, 0.2111394350208904, 0.20661861269867274, 0.32135579391832025, 0.08635055343142142, 0.14089771127851522, 0.25352202693740006, 0.2057318307553881, 0.29013596988459583, 0.17037875222997706, 0.4691449258527766, 0.2939211614257881, 0.16579483485743748, 0.13565250615459587, 0.5375767074760792, 0.25527325670956963, 0.2570425188954921, 0.1682142792300717, 0.02755648724495032, 0.35454563099730824, 0.29018547580728243, 0.42043350691118836, 0.29920549805711427, 0.32973083172247614], 'mood': [0.010975287336328934, 0.05052749038936629, 0.06288436802275635, 0.12602040980985654, 0.05833680078249164, 0.15373615191884335, 0.11330234947336482, 0.02959202609182878, 0.12181014900134472, 0.043720102392308204, 0.09163465056263914, 0.026521887997421455]}
# {'cat': [0.006792550179552168, 0.006994813241464581, 0.010362805068191943, 0.019581552961940613, 0.026282257323172752, 0.005618815537383162, 0.008830127502439514, 0.008107735786397896, 0.00456597632848716, 0.008845407940578255, 0.002364176500611749, 0.011086893846876868, 0.008563567788236153, 0.01852074176187307, 0.008457080882527817, 0.00729031405859984, 0.03396516070173645, 0.009140460821049946, 0.006137434512054483, 0.002518634701181103, 0.04204293503998807, 0.010477946190462533, 0.007866475835095393, 0.01149165542979849, 0.0012062760247453987, 0.01817578867653644, 0.011390132828436856, 0.023694962514086308, 0.027443521137436, 0.021150050464797156], 'mood': [0.0002209041692490873, 0.0011141531892523682, 0.0030848334738265643, 0.004207565562702525, 0.00207606032671188, 0.006323868614587441, 0.0027921995228617096, 0.0006289015970966199, 0.00571434773467616, 0.0006620997296710181, 0.0018675217866701403, 0.0002675779887203864]}
# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for dir in dirs:
#         if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir):
#             generateNormalisedVectors(global_means, global_vars, dir)
