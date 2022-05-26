import json
from cloud_utils import getPlacesMetadata, cloudUpload, cloudUploadByColumn, cloudReset
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + "/CLOUD_ACCESS/" + "creds.json"


def main(city_dir_name, google_api_key="AIzaSyB1z27ziPvK-fJFinlz_gzgPbPt4XR55Bk"):
    with open(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/" + city_dir_name + "/profiles.json", 'r') as file:
        data = json.load(file)['sights']
        for i in range(len(data)):
            new_params = list()
            for param in data[i]['cat_params']:
                new_params.append(round(param, 6))
            data[i]['cat_params'] = new_params
            new_params = list()
            for param in data[i]['global_cat_params']:
                new_params.append(round(param, 6))
            data[i]['global_cat_params'] = new_params
            new_params = list()
            for param in data[i]['mood_params']:
                new_params.append(round(param, 6))
            data[i]['mood_params'] = new_params
            new_params = list()
            for param in data[i]['global_mood_params']:
                new_params.append(round(param, 6))
            data[i]['global_mood_params'] = new_params
            data[i]['popularity'] = round(data[i]['popularity'], 4)
            if 'duration' in data[i]:
                data[i]['duration'] = round(data[i]['duration'], 3)
        cloudUpload(city_dir_name, data, data_type='sights')
        # cloudUploadByColumn(city_dir_name, data, column='cat_params', data_type='sights')
        # cloudUploadByColumn(city_dir_name, data, column='quote', data_type='sights')
    # upload directories to google cloud?
    return


def isMetadataGathered(city_dir):
    if os.path.exists(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/" + city_dir + '/text.json'):
        return True
    return False


def isTextMetadataFinal(dir):
    with open(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/" + dir + '/text.json') as file:
        data = json.load(file)
    if 'sights' in data:
        return True
    return False


def isTextFinal(dir):
    with open(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/" + dir + '/text.json') as file:
        data = json.load(file)
    if 'google' not in data['sights'][0]['text'] or len(data['sights'][0]['text']['google']) < 8:
        return False
    return True


def isAnalyzeDone(dir):
    with open(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/" + dir + '/profiles.json') as file:
        data = json.load(file)['sights']
    if 'mood_params' in data[0]:
        return True
    return False


# cloudReset()
#
# done = True
# for _, dirs, _ in os.walk(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/"):
#     for city in dirs:
#         if isMetadataGathered(city) and isTextMetadataFinal(city) and isTextFinal(city):
#             # if city == "TEL_AVIV_GD_IL":
#             #     done = True
#             if done:
#                 print(city)
#                 main(city)


print("GOLDEN_SELECTION")
main("GOLDEN_SELECTION")
