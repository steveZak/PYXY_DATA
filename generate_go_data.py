import json
import os

cities = dict() # cities
for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
    for city_dir in dirs:
        if os.path.exists(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/city_config.json"):
            with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/city_config.json") as file:
                data = json.load(file)
        cities[city_dir] = data
with open(os.getcwd() + "/CITY_DATABASES/go_cities.json", 'w') as file:
        json.dump(cities, file, indent=2)

places = dict() # places
for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
    for city_dir in dirs:
        if os.path.exists(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/city_config.json"):
            with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/profiles.json") as file:
                data = json.load(file)
            for i in range(len(data['sights'])):
                data['sights'][i].pop("orig_name", None)
                data['sights'][i].pop("cat_params", None)
                data['sights'][i].pop("mood_params", None)
                data['sights'][i].pop("noncat_params", None)
                data['sights'][i].pop("num_google_reviews", None)
                data['sights'][i].pop("quote", None)
                data['sights'][i].pop("phone", None)
                data['sights'][i].pop("int_phone", None)
                data['sights'][i].pop("hours", None)
                data['sights'][i].pop("address", None)
                data['sights'][i].pop("top_cats", None)
                if len(data['sights'][i]["photos"])>0:
                    data['sights'][i]["photo"] = data['sights'][i]["photos"][0]
                else:
                    data['sights'][i]["photo"] = None
                data['sights'][i].pop("photos", None)
                data['sights'][i].pop("website", None)
                data['sights'][i].pop("quote_source", None)
            places[city_dir] = data
with open(os.getcwd() + "/CITY_DATABASES/go_places.json", 'w') as file:
        json.dump(places, file, indent=2)

dist_mats = dict() # dist_mat
for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
    for city_dir in dirs:
        with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/distance.json") as file:
            data = json.load(file)
        data.pop("transit_dist_walk_matrix", None)
        data.pop("transit_time_matrix", None)
        data.pop("cycling_dist_matrix", None)
        data.pop("cycling_time_matrix", None)
        dist_mats[city_dir] = data
with open(os.getcwd() + "/CITY_DATABASES/dist_mat.json", 'w') as file:
        json.dump(dist_mats, file, indent=2)