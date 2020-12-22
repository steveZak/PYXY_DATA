import requests
import json
import os
from google.cloud import storage
from PIL import Image
import io
# from analyze import isMetadataGathered, isTextMetadataFinal, isTextFinal, isAnalyzeDone


def getImage(reference, max_height, api_key):
    query = "https://maps.googleapis.com/maps/api/place/photo?maxheight=" + str(max_height)\
            + "&photoreference=" + reference + "&key=" + api_key
    return requests.get(query)


# def uploadToBucket(client, bucket, city_dir_name, place_id, reference, name, api_key):
#     name = city_dir_name + '/' + place_id + '/' + name
#     if not storage.Blob(bucket=bucket, name=name).exists(client):
#         img = getImage(reference, 1600, api_key)
#         img = io.BytesIO(img.content)
#         blob = bucket.blob(name)
#         blob.upload_from_file(img)


def uploadToBucketIfEmpty(client, bucket, city_dir_name, place_id, reference, name, api_key):
    name = city_dir_name + '/' + place_id + '/' + name
    img = getImage(reference, 1600, api_key)
    img = io.BytesIO(img.content)
    blob = bucket.blob(name)
    blob.upload_from_file(img)


# def main(city_dir_name, api_key="AIzaSyB1z27ziPvK-fJFinlz_gzgPbPt4XR55Bk"):
#     with open("CITY_DATABASES/" + city_dir_name + "/profiles.json") as file:
#         profiles = json.load(file)
#     client = storage.Client()
#     bucket = client.get_bucket('pyxy_place_images')
#     for profile in profiles['sights']:
#         place_id = profile['place_id']
#         for photo in profile['photos']:
#             reference = photo['photo_reference']
#             author = photo['html_attributions'][0].split('>') if len(photo['html_attributions']) > 0 else ""
#             if len(author) == 1:
#                 author = author[0]
#             else:
#                 author = author[1][:-3] if len(author) > 0 else ""
#             name = reference + '|' + author
#             uploadToBucket(client, bucket, city_dir_name, place_id, reference, name, api_key)


def uploadImages(city_dir_name, api_key="AIzaSyB1z27ziPvK-fJFinlz_gzgPbPt4XR55Bk"):
    if city_dir_name is None:
        with open("CITY_DATABASES/GOLDEN_SELECTION/profiles.json") as file:
            profiles = json.load(file)
    else:
        with open("CITY_DATABASES/" + city_dir_name + "/profiles.json") as file:
            profiles = json.load(file)
    client = storage.Client()
    print('ok')
    bucket = client.get_bucket('pyxy_place_images')
    print('sloooow')
    for profile in profiles['sights']:
        place_id = profile['place_id']
        print(profile['name'])
        blobs = client.list_blobs(bucket, prefix=city_dir_name + '/' + place_id)
        if not any(True for _ in blobs):
        # if True:
            print(profile['name'])
            print(city_dir_name)
            for photo in profile['photos']:
                reference = photo['photo_reference']
                author_full = photo['html_attributions'][0].split('>') if len(photo['html_attributions']) > 0 else ""
                author_link = ""
                if len(author_full) == 1:
                    author = author_full[0]
                else:
                    author = author_full[1][:-3] if len(author_full) > 0 else ""
                    author_link = author_full[0].split("\"")[1] if len(author_full) > 0 else ""
                name = reference + '|' + author + '|' + author_link.split('/')[-1]
                uploadToBucketIfEmpty(client, bucket, city_dir_name, place_id, reference, name, api_key)


# def renameImages(city_dir_name, api_key="AIzaSyB1z27ziPvK-fJFinlz_gzgPbPt4XR55Bk"):
#     if city_dir_name is None:
#         with open("CITY_DATABASES/GOLDEN_SELECTION/profiles.json") as file:
#             profiles = json.load(file)
#     else:
#         with open("CITY_DATABASES/" + city_dir_name + "/profiles.json") as file:
#             profiles = json.load(file)
#     client = storage.Client()
#     bucket = client.get_bucket('pyxy_place_images')
#     for profile in profiles['sights']:
#         place_id = profile['place_id']
#         print(profile['name'])
#         print(city_dir_name)
#         blobs = client.list_blobs(bucket, prefix=city_dir_name + '/' + place_id)
#         for blob in blobs:
#             photo = None
#             for img in profile["photos"]:
#                 if img['photo_reference'] in blob.id:
#                     photo = img
#                     break
#             if photo is None:
#                 print("wtf")
#                 continue
#             reference = photo['photo_reference']
#             author_full = photo['html_attributions'][0].split('>') if len(photo['html_attributions']) > 0 else ""
#             author_link = ""
#             if len(author_full) == 1:
#                 author = author_full[0]
#             else:
#                 author = author_full[1][:-3] if len(author_full) > 0 else ""
#                 author_link = author_full[0].split("\"")[1] if len(author_full) > 0 else ""
#             name = reference + '|' + author + '|' + author_link.split('/')[-1]
#             new_blob = bucket.rename_blob(blob, city_dir_name + '/' + place_id + '/' + name)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + "/CLOUD_ACCESS/" + "creds.json"

# reached = False
# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES/"):
#     for city in dirs:
#         if isMetadataGathered(city) and isTextMetadataFinal(city) and isTextFinal(city) and isAnalyzeDone(city) and reached:
#             uploadImages(city)
#         if city == "FUZHOU_FJ_CN":
#             reached = True
