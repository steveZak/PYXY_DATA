import pymysql
import json
import requests
import csv
import os


def getPlacesMetadata(city_dir_name, api_key):
    sights = list()
    city_dir = os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/"+city_dir_name
    quote_data = getGoogleQuote(city_dir)
    with open(city_dir + "/params.json") as file:
        params_data = json.load(file)['sights']
    for place in params_data:
        profile = dict()
        place_id = place['place_id']
        name = place['name']
        cat_params = place['cat_params']
        mood_params = place['mood_params']
        quote = quote_data[place_id]
        details = getDetailsByPlaceId(place_id, api_key)
        if 'result' not in details:
            break
        else:
            place_data = details['result']
        orig_name = place_data['name'] if 'name' in place_data else name
        phone = place_data['formatted_phone_number'] if 'formatted_phone_number' in place_data else ''
        int_phone = place_data['international_phone_number'] if 'international_phone_number' in place_data else ''
        hours = place_data['opening_hours']['periods'] if 'opening_hours' in place_data else ''
        coordinates = place_data['geometry']['location'] if 'geometry' in place_data else ''
        address = place_data['formatted_address'] if 'formatted_address' in place_data else ''
        photos = place_data['photos'] if 'photos' in place_data else ''
        rating = place_data['rating'] if 'rating' in place_data else ''
        profile['name'] = name
        profile['orig_name'] = orig_name
        profile['place_id'] = place_id
        profile['cat_params'] = cat_params
        # profile['noncat_params'] = noncat_params
        profile['mood_params'] = mood_params
        profile['quote'] = quote
        profile['phone'] = phone
        profile['int_phone'] = int_phone
        profile['hours'] = hours
        profile['coordinates'] = coordinates
        profile['address'] = address
        profile['photos'] = photos
        profile['rating'] = rating
        sights.append(profile)
    profiles = dict()
    profiles['sights'] = sights
    return profiles


def getDetailsByPlaceId(place_id, api_key):
    query = "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + place_id + "&key=" + api_key
    return requests.get(query).json()


def getGoogleQuote(city_dir):
    google_quotes = dict()
    with open(city_dir + "/text.csv", 'r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            elts = row[0].split('}')
            place_id = elts[0][1:]
            quote = elts[3][3:]
            google_quotes[place_id] = quote
    return google_quotes


def cloudUpload(db, data, data_type='sights', socket='cloudsql/',
                project_name='my-project-1564769957780:us-central1:pyxy-v1', user='root', password='jtdMtBacur3lCDvK'):
    conn = pymysql.connect(unix_socket=socket + project_name, user=user, password=password, db=db)
    cur = conn.cursor()
    sql_query = "DELETE FROM " + data_type
    cur.execute(sql_query)
    for sight in data:
        if sight['rating'] is None:
            continue
        for key in sight.keys():
            sight[key] = str(sight[key]).replace("'", "''")
        if db == "GOLDEN_SELECTION":
            place_query = "('" + sight['place_id'] + "', '" + sight['name'] + "', '" + sight['city_id'] + "', '" + sight['orig_name']\
                          + "', '" + sight['quote'] + "', '" + sight['phone'] + "', '" + sight['int_phone']\
                          + "', '" + sight['address'] + "', '" + sight['hours'] + "', '" + sight['coordinates']\
                          + "', " + sight['rating'] + ", " + sight['popularity'] + ", '" + sight['cat_params'] + "', '" + sight['mood_params'] + "', '" + sight['global_cat_params'] + "', '"\
                          + sight['global_mood_params'] + "')"  # noncat_params missing for now
        else:
            place_query = "('" + sight['place_id'] + "', '" + sight['name'] + "', '" + sight['orig_name'] \
                          + "', '" + sight['quote'] + "', '" + sight['phone'] + "', '" + sight['int_phone'] \
                          + "', '" + sight['address'] + "', '" + sight['hours'] + "', '" + sight['coordinates'] + "', '" + sight['top_cats'] \
                          + "', " + sight['rating'] + ", " + sight['popularity'] + ", " + sight['duration'] + ", '" + sight['cat_params'] + "', '" + sight['mood_params'] + "', '" + sight['global_cat_params'] + "', '"\
                          + sight['global_mood_params'] + "')"  # noncat_params missing for now
        # check if place already exists in the table
        # if not cur.execute("SELECT 1 FROM sights WHERE Place_ID = '" + sight.get('place_id')+"'"):
        sql_query = "INSERT INTO " + data_type + " VALUES "
        sql_query += place_query
        # print(sql_query)
        cur.execute(sql_query)
        conn.commit()
    return 0


def cloudUploadByColumn(db, data, column, data_type='sights', socket='cloudsql/',
                        project_name='my-project-1564769957780:us-central1:pyxy-v1', user='root',
                        password='jtdMtBacur3lCDvK'):
    conn = pymysql.connect(unix_socket=socket + project_name, user=user, password=password, db=db)
    cur = conn.cursor()
    for sight in data:
        for key in sight.keys():
            sight[key] = str(sight[key]).replace("'", "''")
        sql_query = "UPDATE " + data_type + " SET " + column + " = '" + sight[column]\
                    + "' WHERE place_id = " + "'"+sight['place_id'] + "'"
        # print(sql_query)
        cur.execute(sql_query)
        conn.commit()
    return 0


def cloudReset(socket='cloudsql/', project_name='my-project-1564769957780:us-central1:pyxy-v1',
               user='root', password='jtdMtBacur3lCDvK'):
    conn = pymysql.connect(unix_socket=socket + project_name, user=user, password=password, db=None)
    cur = conn.cursor()
    cur.execute("SHOW DATABASES")
    databases = cur.fetchall()
    for db in databases:
        try:
            cur.execute("DROP DATABASE IF EXISTS " + db[0])
        except pymysql.Error:
            print(db[0] + ' could not be removed')
    city_list = list()
    for _, dirs, _ in os.walk(os.getcwd() + "/PYXY_DATA_COLLECT/CITY_DATABASES/"):
        for dir in dirs:
            city_list.append(dir)
    for city_dir_name in city_list:
        cur.execute("DROP DATABASE IF EXISTS " + city_dir_name)
        cur.execute("CREATE DATABASE " + city_dir_name)
        cur.execute("USE " + city_dir_name)
        if city_dir_name == "GOLDEN_SELECTION":
            cur.execute("CREATE TABLE sights( "
                        + "place_id varchar(100), name varchar(100), city_id varchar(80), orig_name varchar(100), quote varchar(500), "
                        + "phone varchar(30), int_phone varchar(30), address varchar(250), "
                        + "hours varchar(2500), coordinates varchar(80), "
                        + "rating float, popularity float, cat_params varchar(500), "
                        + "mood_params varchar(400), global_cat_params varchar(500), "
                        + "global_mood_params varchar(400)"
                        + ")")
        else:
            cur.execute("CREATE TABLE sights( "
                        + "place_id varchar(100), name varchar(100), orig_name varchar(100), quote varchar(500), "
                        + "phone varchar(30), int_phone varchar(30), address varchar(250), "
                        + "hours varchar(2500), coordinates varchar(80), top_cats varchar(100),"
                        + "rating float, popularity float, duration float, cat_params varchar(500),"
                        + "mood_params varchar(400), global_cat_params varchar(500), "
                        + "global_mood_params varchar(400)"
                        + ")")


# use to resolve city dir ambiguity
def getCityDir(city_name, sight_coordinates):
    with open("CITY_DATABASES/city_dir_names.json") as file:
        city_data = json.load(file)
    keys = list()
    dists = list()
    for city in city_data.keys():
        if city_data[city]['name'] == city_name:
            keys.append(city)
    if len(keys) == 1:
        return keys[0]
    else:
        for key in keys:
            dist = abs(city_data[key]['coordinates']['lat'] - sight_coordinates['lat']) \
                   + abs(city_data[key]['coordinates']['lng'] - sight_coordinates['lng'])
            dists.append(dist)
    if min(dists) > 1:
        return "Nearest city not found"
    else:
        return keys[dists.index(min(dists))]


# def cloudDownload(db, data_type, socket='cloudsql/',
#                   project_name='my-project-1564769957780:us-central1:routing-app-v1', user='root', password='121314'):
#     db = db.replace(" ", "_")
#     conn = pymysql.connect(unix_socket=socket+project_name, user=user, password=password, db=db)
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM sights")
#     rows = cur.fetchall()
#     return rows
