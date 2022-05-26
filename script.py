import os
import json
# from analyze import isMetadataGathered, isTextMetadataFinal, isTextFinal, isAnalyzeDone
import numpy as np
import random

# copy profiles + quotes to golden selection

# new_global_sights = {'sights': list()}
# with open(os.getcwd() + "/CITY_DATABASES/" + "GOLDEN_CO_US" + "/profiles.json", 'r') as old_file:
#     global_sights = json.load(old_file)
#     for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#         for city_dir in dirs:
#             with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/profiles.json", 'r') as file:
#                 local_sights = json.load(file)
#                 for i in range(len(global_sights['sights'])):
#                     for sight in local_sights['sights']:
#                         if sight['place_id'] == global_sights['sights'][i]['place_id']:
#                             sight['city_id'] = global_sights['sights'][i]['city_id']
#                             global_sights['sights'][i] = sight
#                             break
# with open(os.getcwd() + "/CITY_DATABASES/" + "GOLDEN_CO_US" + "/profiles.json", 'w') as new_file:
#     json.dump(global_sights, new_file, indent=1)

# copy new quotes from profiles
# for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
#     for city_dir in dirs:
#         places = list()
#         if city_dir == "NEW_YORK_CITY_NY_US":
#             print(city_dir)
#             with open(os.getcwd()+"/CITY_DATABASES/"+city_dir+"/profiles.json", 'r') as file_from:
#                 with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/text.json", 'r') as file_to:
#                     data_from = json.load(file_from)
#                     data_to = json.load(file_to)
#                     data_to_new = list()
#                     for sight in data_from['sights']:
#                         quote = sight['quote']
#                         place_id = sight['place_id']
#                         for sight_out in data_to:
#                             if place_id == sight_out['place_id']:
#                                 if quote not in sight_out['description']:
#                                     description = sight_out['description'] + ' ' + quote
#                                     sight_out['description'] = description
#                                     data_to_new.append(sight_out)
#                                     break
#                                 data_to_new.append(sight_out)
#             with open(os.getcwd()+"/CITY_DATABASES/"+city_dir+"/text.json", 'w') as json_file:
#                 json.dump(data_to_new, json_file, indent=1)

# copy directories to golden selection (conditionally limit later)
# global_sights = {"sights": list()}
# for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
#     for city_dir in dirs:
#         if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir)\
#                 and isTextFinal(city_dir) and isAnalyzeDone(city_dir):
#             with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/profiles.json") as file:
#                 i = 0
#                 for sight in json.load(file)['sights']:
#                     if i > 30:
#                         break
#                     # if random.random() < 0.5:
#                     sight['city_id'] = city_dir
#                     global_sights['sights'].append(sight)
#                     i += 1
# sum_cat_params = {}
# for sight in global_sights['sights']:
#     if sight['city_id'][-2:] == "CN":
#         sum_cat_params[sight['place_id']] = 20 * (sum(sight['global_cat_params']) + sight['num_google_reviews'] * 75 / 800)
#         continue
#     sum_cat_params[sight['place_id']] = sum(sight['cat_params']) + sight['num_google_reviews']*75/800
#     print(sum_cat_params[sight['place_id']])
# global_sights['sights'].sort(key=lambda x: sum_cat_params[x['place_id']], reverse=True)
# global_sights['sights'] = global_sights['sights'][:int(len(global_sights['sights'])/3)]
# with open(os.getcwd() + "/CITY_DATABASES/GOLDEN_SELECTION/" + "profiles.json", 'w') as file_out:
#     json.dump(global_sights, file_out, indent=2)
# #
# # rank cities by number of sights in golden selection
# cities = {}
# with open(os.getcwd() + "/CITY_DATABASES/GOLDEN_SELECTION/" + "profiles.json") as file:
#     sights = json.load(file)['sights']
# for sight in sights:
#     if sight['city_id'] not in cities.keys():
#         cities[sight['city_id']] = 1
#         continue
#     cities[sight['city_id']] += 1
# cities = {k: v for k, v in sorted(cities.items(), key=lambda item: item[1], reverse=True)}
# for city in cities.keys():
#     print(city + " " + str(cities[city]))

# remove (Translated by Google tags)
# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for city_dir in dirs:
#         if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir)\
#          and isTextFinal(city_dir):
#             print(city_dir)
#             with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/text.json") as file:
#                 sights = json.load(file)['sights']
#                 for i in range(len(sights)):
#                     google_reviews = sights[i]['text']['google']
#                     for j in range(len(google_reviews)):
#                         if "(Translated by Google)" in google_reviews[j]:
#                             google_reviews[j] = google_reviews[j][23:]
#                             if "(Original)" in google_reviews[j]:
#                                 google_reviews[j] = google_reviews[j].split("(Original)")[0]
#                     sights[i]['text']['google'] = google_reviews
#             with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/text.json", 'w') as file_out:
#                 json.dump(sights, file_out, indent=2)

# check finalised cities
# global_sights = {"sights": list()}
# for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
#     for city_dir in dirs:
#         # print(city_dir)
#         if isMetadataGathered(city_dir)\
#                 and isTextMetadataFinal(city_dir)\
#                 and not isTextFinal(city_dir):
#             # if not isAnalyzeDone(city_dir):
#              print(city_dir)

# get avg cat_patams and infer duration
# with open(os.getcwd() + "/CITY_DATABASES/GOLDEN_SELECTION/" + "profiles.json") as file:
#     sights = json.load(file)['sights']
# avg_cat_params = None
# for sight in sights:
#     if avg_cat_params is None:
#         avg_cat_params = sight['cat_params']
#     else:
#         avg_cat_params = [avg_param + param for avg_param, param in zip(avg_cat_params, sight['cat_params'])]
# avg_cat_params = [param/len(sights) for param in avg_cat_params]
# print(avg_cat_params)

# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for city in dirs:
#         if isMetadataGathered(city):
#             with open(os.getcwd() + "/CITY_DATABASES/" + city + "/profiles.json") as file:
#                 sights = json.load(file)['sights']
#             for sight in sights:
#                 if sum(sight['mood_params']) == 0 or sum(sight['cat_params']) == 0:
#                     print(sight['name'] + ' ' + city)

min_sights = 60
for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for city in dirs:
        with open(os.getcwd() + "/CITY_DATABASES/" + city + "/profiles.json") as file:
            sights = json.load(file)['sights']
        if len(sights)< min_sights:
            min_sights = len(sights)
        # for sight in sights:
        #     i+=1
        #     # if sight['rating'] == None:
        #     #     print(sight['name'])
        #     #     print(city)
print(min_sights)