import json
import os
from text_mining_utils import getPlaceQuote, getCityName

def main(city_dir):
    city = getCityName(city_dir)
    with open("CITY_DATABASES/" + city_dir + "/profiles.json") as file:
        places = json.load(file)
    if 'quote_source' in places['sights'][1]:
        return
    for i in range(len(places['sights'])):
        quote = getPlaceQuote(places['sights'][i]['place_id'], city)
        if quote == places['sights'][i]['quote']:
            places['sights'][i]['quote_source'] = 'go'
        else:
            if places['sights'][i]['quote'] == "":
                places['sights'][i]['quote'] = quote
                places['sights'][i]['quote_source'] = 'go'
            else:
                print('px')
                places['sights'][i]['quote_source'] = 'px'
    with open("CITY_DATABASES/" + city_dir + "/profiles.json", 'w') as file:
        json.dump(places, file, indent=2)


def isMetadataGathered(city_dir):
    if os.path.exists("CITY_DATABASES/" + city_dir + '/text.json'):
        return True
    return False

done = True
for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
    for dir in dirs:
        if isMetadataGathered(dir) and dir != "ZURICH_ZH_CH" and done:
            print(dir)
            main(dir)
