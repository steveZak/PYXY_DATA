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
{'cat': [0.15983512701554506, 0.11125578879548322, 0.22342023758401322, 0.2313071244902171, 0.3009363305585727, 0.14441289330372456, 0.394635456157532, 0.21065322703575048, 0.20461491524525136, 0.31879038018477274, 0.0853171882375397, 0.13924546238879246, 0.2512256100017176, 0.2026731915561896, 0.28766113402009447, 0.16840819079940733, 0.46603239739430713, 0.2921054046240055, 0.1637632924309885, 0.13468468967734126, 0.5324568510053709, 0.25225076553542614, 0.25712312352645195, 0.16785605257268763, 0.027231167485861543, 0.35140511182630785, 0.2875094078370519, 0.41743196414457656, 0.29599276468955077, 0.32613435803871793], 'mood': [0.01085510141610592, 0.050171447147373906, 0.062392447294834355, 0.1252169291351518, 0.05781338527389534, 0.15204444198973943, 0.11225686682221096, 0.029340639054441623, 0.12087510490979755, 0.04343677810448804, 0.09116442588606377, 0.026244795697652187]}
{'cat': [0.0069478107234248, 0.006984499403720639, 0.010428888248885501, 0.019561708928329254, 0.02587587702983704, 0.005668436043966719, 0.009065469846789055, 0.008166910000407736, 0.004594637163288316, 0.008951958994463029, 0.002303152327334481, 0.010816656257608626, 0.008589787982113715, 0.018188586356662102, 0.008532529972712456, 0.007132208068184087, 0.03374677803694675, 0.00918406005949729, 0.006113043412966385, 0.002554697404373781, 0.041859994652603386, 0.010348453707799096, 0.007936277512047148, 0.011628674155807648, 0.0011706913340832142, 0.017833156060971318, 0.011372367136883487, 0.02361424135605437, 0.02705090986638632, 0.020900548296674693], 'mood': [0.0002200651699646635, 0.0011074680876700833, 0.003045707844193258, 0.004162345723194969, 0.002047996078360623, 0.006244696870574858, 0.002784541772330041, 0.0006231231943879724, 0.005633224779564261, 0.0006726904274077215, 0.0018589891039394592, 0.0002660190041491612]}
for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for dir in dirs:
        if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir):
            generateNormalisedVectors(global_means, global_vars, dir)
