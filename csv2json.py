import csv
import json
import os


def writeFile(dir):
    with open(dir + "/params.json", 'w') as file_out:
        with open(dir + "/params.csv",  'r') as file_in:
            data = dict()
            sights = list()
            for line in file_in.readlines():
                if line[0] is 'a':
                    data['categories'] = line[:-1].split(',')
                else:
                    all_params = line[:-1].split(',')
                    params = all_params[:-1]
                    params = [round(float(i), 4) for i in params]
                    place_id = all_params[-1][1:]
                    sight = dict()
                    sight['place_id'] = place_id
                    sight['name'] = findName(dir, place_id)
                    sight['cat_params'] = params
                    sights.append(sight)
            data['sights'] = sights
            json.dump(data, file_out, indent=2)


def findName(city_dir, place_id):
    with open(city_dir + '/text.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if place_id in row[0]:
                return row[0].split("}")[1][3:]


for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for dir in dirs:
        writeFile(os.getcwd() + "/CITY_DATABASES/" + dir)
