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


for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for dir in dirs:
        if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir):
            print(dir)
            main(dir, 'cat_params')
            main(dir, 'mood_params')

global_means, global_vars = generateGlobalVectors()  # generate mean and variance
print(global_means)
print(global_vars)
{'cat': [0.16014674300006343, 0.11123928675476968, 0.22337489861824122, 0.23048395039734917, 0.3023035239571502, 0.14465734366364563, 0.39567077472202394, 0.2106168160806359, 0.20567279777853809, 0.3192526310264833, 0.08562954321504233, 0.14034080516643996, 0.25169524668864984, 0.20349527228568104, 0.28816560932284874, 0.16869741009965106, 0.4656425962927871, 0.29221498310735017, 0.16402212475565794, 0.13484403586592833, 0.5329244258823, 0.2537919352970189, 0.2572480802628525, 0.1680877313999005, 0.027293560502931656, 0.353031196542122, 0.28763921484711913, 0.41771790601665143, 0.29629817119915297, 0.3277103617790381], 'mood': [0.010867786980335047, 0.05010792215456719, 0.06222057952369998, 0.12491777468736937, 0.057644970513488734, 0.1517921301852328, 0.11217839304763394, 0.029286185602429265, 0.12060362029498813, 0.04341755187811798, 0.09116650817750185, 0.0262185191989822]}
{'cat': [0.00691260405855637, 0.006952597090405478, 0.010372250134986067, 0.019434724427989693, 0.026083956132045238, 0.005661707409197808, 0.009062274363791893, 0.0081651575729299, 0.004636914178068046, 0.008972349034736218, 0.0023607433513003003, 0.011154019746411397, 0.008644858402755863, 0.018220571914275493, 0.008543692855524709, 0.007261143506383286, 0.03409844050667376, 0.009220715248252366, 0.006125262828449511, 0.0025510414997378487, 0.04193288619639573, 0.010534917472145243, 0.00802187696325662, 0.011583713660621928, 0.001180746991245804, 0.018373437547654577, 0.01134915348339586, 0.02377628724143824, 0.02717612752928121, 0.021072314994095155], 'mood': [0.0002199386645044318, 0.0011118102544051035, 0.0030438066741602333, 0.00418933975541896, 0.0020532699765577395, 0.0062992479787119604, 0.002807634620072957, 0.0006237367793460567, 0.005657810911964192, 0.0006737241618087562, 0.0018789148424184416, 0.00026656145623106336]}
for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for dir in dirs:
        if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir):
            generateNormalisedVectors(global_means, global_vars, dir)
