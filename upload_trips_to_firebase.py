import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
import json
import os
# from analyze import isMetadataGathered, isTextMetadataFinal, isTextFinal


def uploadCity(db, city_dir):
    with open('CITY_DATABASES/' + city_dir + '/city_config.json') as file:
        city_config = json.load(file)
    with open('CITY_DATABASES/city_dir_names.json') as file:
        cities = json.load(file)
    with open('CITY_DATABASES/' + city_dir + '/profiles.json') as file:
        sights = json.load(file)['sights']
    with open('CITY_DATABASES/' + city_dir + '/trips.json') as file:
        data = json.load(file)
        theme_trips = data['theme_trips']
        mood_trips = data['mood_trips']
        popularity_trips = data['popularity_trips']
        distance_trips = data['distance_trips']
    short_sights = []
    for sight in sights:
        short_sights.append({"uid": sight['place_id'], "name": sight['name'], "coordinates": sight["coordinates"]})
    short_theme_trips = []
    short_mood_trips = []
    short_popularity_trips = []
    short_distance_trips = []
    for trip in theme_trips:
        short_theme_trips.append({"uid": trip['trip_id']})
    for trip in mood_trips:
        short_mood_trips.append({"uid": trip['trip_id']})
    for trip in popularity_trips:
        short_popularity_trips.append({"uid": trip['trip_id']})
    for trip in distance_trips:
        short_distance_trips.append({"uid": trip['trip_id']})
    db.collection(u'cities').document(city_dir).set({"sights": short_sights}, merge=True)
    # db.collection(u'cities').document(city_dir).set({"theme_trips": short_theme_trips,
    #                                                  "mood_trips": short_mood_trips,
    #                                                  "popularity_trips": short_popularity_trips,
    #                                                  "distance_trips": short_distance_trips}, merge=True)
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
        uid = sight.pop("place_id")
        sight.pop("cat_params")
        sight.pop("noncat_params") if "noncat_params" in sight else None
        sight.pop("photos")
        sight.pop("mood_params")
        sight.pop("num_google_reviews")
        sight.pop("top_cats")
        db.collection(u'sights').document(uid).set(sight)
    return


def main(city_dir):
    db = firestore.client()
    # uploadCity(db, city_dir)
    # uploadTrips(db, city_dir)
    uploadSights(db, city_dir)


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
