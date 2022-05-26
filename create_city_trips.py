# User matching not required (generated below) (Public)
# Featured: theme, mood, popularity, distance  (Data includes city, sights, theme/mood/pop, total distance, ratings
# Designed: custom name trips
# Hot: popular trips (get saved counter for every trip) + made by others (only public)

# User matching required (generate user trips through a cloud functions callback) (Private)
# For you (You might like?)
# Unique to you
# Suggested trips (ie Steve's suggested Portland Trip)
# parameters for suggested trips to learn from user interaction : params (map interaction, global Tinder, saved trips)
#                                                                 cities (map interaction, saved trips)
#                                                                 distance (map_interaction, saved trips)
# map interaction: viewing trips + individual sights
# can save trips and sights
# Also
# Personally made (Manually or speech-generated)
#

# Can display all visited trips to yourself, friends or public


# 10 theme trips per city
# 3 mood, 2 popularity
# always display 2 1 1
# create a global avg vector
# create a new separate sql database
# generate top 10 cats, top 3 moods and 2 pops for each city and generate city trips
# add a condition for them to be close (generate a short route < 20 km total distance ?)
# for each category rank the sight by that cat, pick >4, <9 and rank by distance travelled.
# make a limit on distance < 15 km
# limit to the 10 best ones
# same for mood, pop

# Therefore metadata will include distance travelled

import json
import os
from trips_utils import buildBasicTrips, buildCityConfig


def generateCityTrips(city_dir):
    trips = buildBasicTrips(city_dir)
    with open("CITY_DATABASES/" + city_dir + '/trips.json', 'w') as file:
        json.dump(trips, file, indent=2)


def generateCityConfigs(city_dir):
    config = buildCityConfig(city_dir)
    with open("CITY_DATABASES/" + city_dir + '/city_config.json', 'w') as file:
        json.dump(config, file, indent=2)


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


done = False
# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for dir in dirs:
#         if isMetadataGathered(dir) and isTextMetadataFinal(dir) and isTextFinal(dir) and isAnalyzeDone(dir) and done:
#             print(dir)
#             generateCityTrips(dir)
#         if dir == "SACRAMENTO_CA_US":
#             done = True

# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for city_dir in dirs:
#         if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir) and isTextFinal(city_dir) and not os.path.exists("CITY_DATABASES/" + city_dir + '/trips.json'):
#             print(city_dir)
#             generateCityTrips(city_dir)


def configNeeded(city_dir):
    if os.path.exists("CITY_DATABASES/" + city_dir + '/city_config.json'):
        return False
    return True


# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for city_dir in dirs:
#         # if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir) and isTextFinal(city_dir):
#         if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir) and configNeeded(city_dir):
#             print(city_dir)
#             generateCityTrips(city_dir)


# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for city_dir in dirs:
#         # if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir) and isTextFinal(city_dir):
#         if isMetadataGathered(city_dir) and isTextMetadataFinal(city_dir):
#             print(city_dir)
#             generateCityConfigs(city_dir)


for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for city_dir in dirs:
        generateCityConfigs(city_dir)
