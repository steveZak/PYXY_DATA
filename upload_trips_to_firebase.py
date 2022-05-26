import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
import json
import os
import numpy as np
# from analyze import isMetadataGathered, isTextMetadataFinal, isTextFinal


criteria = ["Amusement", "Animals", "Architecture", "Art", "Beach", "Books", "Cosmopolitan", "Culture", "Engineering", "Family", "Fashion", "Food", "Friends", "Hiking", "History", "Hospitality", "Insta", "Military", "Music", "Movies", "Nature", "Nightlife", "Original", "Religion", "Science", "Shopping", "Sport", "Views", "Walking", "Water"]

mood_criteria = ["Adventuresome", "Entertaining", "Peaceful", "Captivating", "Magical", "Exciting", "Impressive", "Inspiring", "Romantic", "Scary", "Wise", "Sad"]

def uploadCity(db, city_dir):
    with open('CITY_DATABASES/' + city_dir + '/city_config.json') as file:
        city_config = json.load(file)
    with open('CITY_DATABASES/city_dir_names.json') as file:
        cities = json.load(file)
    with open('CITY_DATABASES/' + city_dir + '/profiles.json') as file:
        sights = json.load(file)['sights']
    with open('CITY_DATABASES/trips.json') as file:
        data = json.load(file)
    top_cat_idxs = np.argsort(city_config["cat_params"])[::-1][:10]
    top_cats = np.take(criteria, top_cat_idxs)
    top_mood_idxs = np.argsort(city_config["mood_params"])[::-1][:5]
    top_moods = np.take(mood_criteria, top_mood_idxs)
    short_sights = []
    for sight in sights:
        short_sights.append({"uid": sight['place_id'], "name": sight['name'], "coordinates": sight["coordinates"]})
    short_cat_trips = []
    short_mood_trips = []
    for label in top_cats:
        short_cat_trips.append({"uid": city_dir+"_T_"+label})
    for label in top_moods:
        short_mood_trips.append({"uid": city_dir+"_M_"+label})
    print(short_cat_trips)
    return
    db.collection(u'cities').document(city_dir).set({"cat_params": city_config["cat_params"], "mood_params": city_config["mood_params"], "sights": short_sights, "cat_trips": short_cat_trips, "mood_trips": short_mood_trips}, merge=True)
    # db.collection(u'cities').document(city_dir).set({"sights": short_sights}, merge=True)
    # db.collection(u'cities').document(city_dir).set({"cat_trips": short_cat_trips, "mood_trips": short_mood_trips}, merge=True)
    return


def uploadTrips(db, city_dir):
    with open('CITY_DATABASES/' + city_dir + '/trips.json') as file:
        data = json.load(file)
        theme_trips = data['theme_trips']
        mood_trips = data['mood_trips']
        popularity_trips = data['popularity_trips']
        distance_trips = data['distance_trips']
    for i in range(len(theme_trips)):
        for j in range(len(theme_trips[i]['sights'])):
            sight = theme_trips[i]['sights'][j]
            theme_trips[i]['sights'][j] = {"uid": sight["place_id"], "name": sight["name"], "coordinates": sight["coordinates"]}
        uid = theme_trips[i].pop("trip_id")
        db.collection(u'trips').document(uid).set(theme_trips[i])
    for i in range(len(mood_trips)):
        for j in range(len(mood_trips[i]['sights'])):
            sight = mood_trips[i]['sights'][j]
            mood_trips[i]['sights'][j] = {"uid": sight["place_id"], "name": sight["name"], "coordinates": sight["coordinates"]}
        uid = mood_trips[i].pop("trip_id")
        db.collection(u'trips').document(uid).set(mood_trips[i])
    for i in range(len(popularity_trips)):
        for j in range(len(popularity_trips[i]['sights'])):
            sight = popularity_trips[i]['sights'][j]
            popularity_trips[i]['sights'][j] = {"uid": sight["place_id"], "name": sight["name"], "coordinates": sight["coordinates"]}
        uid = popularity_trips[i].pop("trip_id")
        db.collection(u'trips').document(uid).set(popularity_trips[i])
    for i in range(len(distance_trips)):
        for j in range(len(distance_trips[i]['sights'])):
            sight = distance_trips[i]['sights'][j]
            distance_trips[i]['sights'][j] = {"uid": sight["place_id"], "name": sight["name"], "coordinates": sight["coordinates"]}
        uid = distance_trips[i].pop("trip_id")
        db.collection(u'trips').document(uid).set(distance_trips[i])
    return


def uploadSights(db, city_dir):
    with open('CITY_DATABASES/' + city_dir + '/profiles.json') as file:
        sights = json.load(file)['sights']
    for sight in sights:
        uid = sight["place_id"]
        sight.pop("cat_params")
        sight.pop("noncat_params") if "noncat_params" in sight else None
        sight.pop("photos")
        sight.pop("mood_params")
        sight.pop("num_google_reviews")
        sight.pop("top_cats")
        sight["city_id"] = city_dir 
        db.collection(u'sights').document(uid).set(sight)
    return


def main(city_dir):
    db = firestore.client()
    uploadCity(db, city_dir)
    # uploadTrips(db, city_dir)
    # uploadSights(db, city_dir)


cred = credentials.Certificate('CLOUD_ACCESS/my-project-1564769957780-firebase-adminsdk-3edlt-66c12201bf.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

done = True
for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for city_dir in dirs:
        print(city_dir)
        main(city_dir)
        
        # if city_dir == "LILLE_HF_FR":
        #     done = True
