# from google.cloud import vision
import requests
import wikipedia
import os
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
# from google.cloud import translate_v2 as translate


##################
# Naming utils
##################

def getCityName(city_dir_name):
    return city_dir_name.replace("_", " ")[:-6]


##################
# Location search  utils
##################

def gatherPlaceData(api_key, data_type, city):
    if data_type == "sights":
        query = "things to see in "
    elif data_type == "foods":
        query = "places to eat at "
    # cloud_city_id = city.replace(" ", "_")
    query += city
    return placeSearch(api_key, query)


def placeSearch(api_key, query):
    query = query.replace(" ", "+")
    query = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="\
        + query + "&key=" + api_key
    r = requests.get(query)
    time.sleep(3)
    x = r.json()
    destinations = x['results']
    while 'next_page_token' in x:
        query_next = "https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken="\
            + x['next_page_token'] + "&key=" + api_key
        r = requests.get(query_next)
        time.sleep(3)
        x = r.json()
        destinations.extend(x['results'])
    return destinations


# maybe complete nearby town search
# def nearbySearch(api_key, query):
#     query = query.replace(" ", "+")
#     query = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?query="\
#         + query + "&key=" + api_key
#     r = requests.get(query)
#     x = r.json()
#     destinations = x['results']
#     return destinations

##################
# Local database utils
##################


def getProfiles(place, city, google_api_key):
    google_quote = getPlaceQuote(place['place_id'], city)
    formatted_phone_number, international_phone_number,\
        website, hours, photos = getPlaceDetails(place, google_api_key)
    return {'name': place['name'],
            'orig_name': place['name'],
            'place_id': place['place_id'],
            'cat_params': [],
            'noncat_params': [],
            'quote': google_quote,
            'phone': formatted_phone_number,
            'int_phone': international_phone_number,
            'hours': hours,
            'coordinates': place['geometry']['location'] if 'geometry' in place else {},
            'address': place['formatted_address'] if 'formatted_address' in place else '',
            'photos': photos,
            'rating': place['rating'] if 'rating' in place else None,
            'website': website}


def getText(place, city, website):
    wiki_text = getPlaceWikiText(place['name'], city)
    brit_text = getBrittanicaText(place['name'])
    google_quote = getPlaceQuote(place['place_id'], city)
    google_tags = str(place['types']) if "types" in place else ""
    return {'place_id': place['place_id'], 'name': place['name'],
            'text': {'wiki': wiki_text, 'brit': brit_text, 'quote': google_quote, 'tags': google_tags,
                     'website': {'source': website, 'content': ''}}}


def getWebsite(place_id, api_key):
    query = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id\
                      + "&fields=website&key=" + api_key
    rsp = requests.get(query).json()
    return rsp['result']['website'] if 'result' in rsp and 'website' in rsp['result'] else ''


# def getPlaceGoogleReviews(place, api_key):
#     query = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place['place_id']\
#               + "&fields=review&key=" + api_key
#     rsp = requests.get(query).json()
#     reviews = list()
#     if "reviews" not in rsp['result']:
#         return reviews
#     for review in rsp['result']['reviews']:
#         if 'language' not in review or review['language'] is 'en':
#             reviews.append(review['text'])
#         else:
#             reviews.append(getTranslatedText(review['text']))
#     return reviews


def getPlaceDetails(place, api_key):
    query = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place['place_id'] \
            + "&fields=formatted_phone_number,international_phone_number,website,opening_hours,photo&key=" + api_key
    rsp = requests.get(query).json()
    fields = rsp['result']
    formatted_phone_number = fields['formatted_phone_number'] if 'formatted_phone_number' in fields else ''
    international_phone_number = fields['international_phone_number'] if 'international_phone_number' in fields else ''
    website = fields['website'] if 'website' in fields else ''
    hours = fields['opening_hours']['periods'] if 'opening_hours' in fields else ''
    photos = fields['photos'] if 'photos' in fields else ''
    return formatted_phone_number, international_phone_number, website, hours, photos


def isEnglish(text):
    tr_client = translate.Client()
    res = tr_client.detect_language(text)
    return res['language'] == 'en'


def getTranslatedText(text):
    tr_client = translate.Client()
    res = tr_client.translate(text, target_language='en')
    return res['translatedText']


def getPlaceQuote(place_id, city):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver = os.getcwd() + "/chromedriver"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    url = "https://www.google.com/maps/search/?api=1&query=" + city + "&query_place_id=" + place_id
    driver.get(url)
    time.sleep(1.5)
    elt = driver.find_elements_by_xpath("//div[contains(@class,'section-editorial-quote')]")
    quote = elt[0].text if len(elt) > 0 else ""
    driver.quit()
    return quote


def getBrittanicaText(place):
    query = "https://www.britannica.com/topic/" + place.title().replace(' ', '-')
    content = requests.get(query)
    if content.status_code == 404:
        return ''
    soup = BeautifulSoup(content.text, 'html.parser')
    table = soup.findAll('section', attrs={"id": "ref1"})
    text = ""
    for elt in table:
        text += elt.text + ' '
    return text


def getPlaceWikiText(place, city):
    try:
        if city in place:
            return wikipedia.page(place).content
        else:
            return wikipedia.page(place + " " + city).content
    except wikipedia.exceptions.DisambiguationError as e:
        return ""
    except wikipedia.exceptions.PageError as e2:
        return ""


def getGooglePopularity(place_id, city):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver = os.getcwd() + "/chromedriver"
    # driver = webdriver.Chrome(executable_path=chrome_driver)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    url = "https://www.google.com/maps/search/?api=1&query=" + getCityName(city) + "&query_place_id=" + place_id
    driver.get(url)
    num_reviews = 0
    try:
        elt_present = EC.presence_of_element_located((By.CLASS_NAME, "jqnFjrOWMVU__button.gm2-caption"))
        WebDriverWait(driver, 3).until(elt_present)
        buttons = driver.find_elements_by_class_name("jqnFjrOWMVU__button.gm2-caption")
        for button in buttons:
            if len(button.text) > 0 and button.text != 'Directions':
                num_reviews = int(button.text.split(' ')[0].replace(',', ''))
            else:
                button = driver.find_element_by_class_name("gm2-caption")
                if len(button.text) > 0 and button.text != 'Directions':
                    num_reviews = int(button.text.split(' ')[0].replace(',', ''))
            break
    except exceptions.TimeoutException:
        return 0.125
    except exceptions.ElementNotInteractableException:
        return 0.125
    driver.quit()
    return num_reviews


def getGoogleReviews(place_id, city):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver = os.getcwd() + "/chromedriver"
    # driver = webdriver.Chrome(executable_path=chrome_driver)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    url = "https://www.google.com/maps/search/?api=1&query=" + getCityName(city) + "&query_place_id=" + place_id
    driver.get(url)
    try:
        elt_present = EC.presence_of_element_located((By.CLASS_NAME, "jqnFjrOWMVU__button.gm2-caption"))
        WebDriverWait(driver, 5).until(elt_present)
        button = driver.find_element_by_class_name("jqnFjrOWMVU__button.gm2-caption")
        button.click()
    except exceptions.TimeoutException:
        pass
    except exceptions.ElementNotInteractableException:
        pass
    time.sleep(0.5)
    elts = None
    for i in range(500):
        elts = driver.find_elements_by_class_name("section-review-review-content")
        if len(elts) > 500:
            break
        if len(elts) > 0:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", elts[-1])
            except exceptions.StaleElementReferenceException:
                pass
        time.sleep(0.1)
    reviews = list()
    for i in range(len(elts)):
        if i > 500:
            break
        reviews.append(elts[i].text)
        i += 1
    driver.quit()
    return reviews


def getTripText(place, city_dir):
    chrome_driver = os.getcwd() + "/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    query = "https://www.google.com/search?q=" + place.replace(' ', '+') + '+'\
            + getCityName(city_dir).replace(' ', '+') + "+tripadvisor"
    driver.get(query)
    elts = driver.find_elements_by_tag_name('a')
    for elt in elts:
        if 'tripadvisor' in elt.text:
            url = elt.get_attribute("href")
            if 'Attraction_Review' in url:
                break
    else:
        return ['']
    # goes to tripadvisor
    checked_urls = list()
    checked_urls.append(url)
    driver.get(url)
    elts_reviews = driver.find_elements_by_class_name("location-review-review-list-parts-ExpandableReview__reviewText--gOmRC")
    if len(elts_reviews) == 0:
        elts_reviews = driver.find_elements_by_class_name("IRsGHoPm")
    elts1 = driver.find_elements_by_class_name("attractions-attraction-detail-travelers-talk-about-TravelersTalkAbout__snippetRow--1Y69a attractions-attraction-detail-travelers-talk-about-TravelersTalkAbout__cx_brand_refresh_phase2--2XDqO")
    elts2 = driver.find_elements_by_class_name("attractions-attraction-review-atf-overview-card-AttractionReviewATFOverviewCard__section--2uMTX")
    text_reviews = list()
    text1, text2 = "", ""
    texts = list()
    try:
        for elt in elts_reviews:
            text_reviews.append(elt.text)
        for elt1 in elts1:
            text1 += elt1.text + ' '
        for elt2 in elts2:
            text2 += elt2.text + ' '
    except exceptions.StaleElementReferenceException:
        print('Stale element exception encountered')
    texts.extend([text1, text2])
    texts.extend(text_reviews)
    elts_buttons = list()
    time.sleep(0.5)
    elts_buttons.extend(driver.find_elements_by_class_name("pageNum.cx_brand_refresh_phase2"))
    next_idx = 2
    next_button = None
    for elt_button in elts_buttons:
        if elt_button.text == str(next_idx):
            next_button = elt_button
            break
    while len(texts) < 500 and next_button is not None:
        text_reviews = list()
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", next_button)
        next_idx += 1
        if driver.current_url not in checked_urls:
            checked_urls.append(driver.current_url)
            time.sleep(0.5)
            elts_reviews = driver.find_elements_by_class_name(
                "location-review-review-list-parts-ExpandableReview__reviewText--gOmRC")
            if len(elts_reviews) == 0:
                elts_reviews = driver.find_elements_by_class_name("IRsGHoPm")
            for elt in elts_reviews:
                try:
                    if elt.text not in text_reviews and elt.text not in texts:
                        text_reviews.append(elt.text)
                except exceptions.StaleElementReferenceException:
                    pass
            texts.extend(text_reviews)
        try:
            time.sleep(0.5)
            elts_buttons = driver.find_elements_by_class_name("pageNum.cx_brand_refresh_phase2")
            next_button = None
            for elt_button in elts_buttons:
                if elt_button.text == str(next_idx):
                    next_button = elt_button
                    break
        except exceptions.StaleElementReferenceException:
            pass
    driver.quit()
    return texts


def getYelpText(place, city_dir):
    chrome_driver = os.getcwd() + "/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    query = "https://www.google.com/search?q=" + place.replace(' ', '+') + '+'\
            + getCityName(city_dir).replace(' ', '+') + "+yelp"
    driver.get(query)
    elts = driver.find_elements_by_tag_name('a')
    for elt in elts:
        if 'yelp' in elt.text:
            url = elt.get_attribute("href")
            break
    else:
        return ['']
    # goes to yelp
    checked_urls = list()
    checked_urls.append(url)
    driver.get(url)
    elts_high_reviews = driver.find_elements_by_class_name("lemon--p__373c0__3Qnnj.text__373c0__2Kxyz.text-color--normal__373c0__3xep9.text-align--left__373c0__2XGa-.text-display--paragraph__373c0__1t3BO")
    elts_reviews = driver.find_elements_by_class_name("lemon--p__373c0__3Qnnj.text__373c0__2Kxyz.comment__373c0__3EKjH.text-color--normal__373c0__3xep9.text-align--left__373c0__2XGa-")
    text_reviews = list()
    texts = list()
    try:
        for elt in elts_high_reviews:
            text_reviews.append(elt.text)
        for elt in elts_reviews:
            text_reviews.append(elt.text)
    except exceptions.StaleElementReferenceException:
        print('Stale element exception encountered')
    texts.extend(text_reviews)
    elts_buttons = list()
    elts_buttons.extend(driver.find_elements_by_class_name("lemon--div__373c0__1mboc.pagination-link-container__373c0__23Bf9.border-color--default__373c0__3-ifU"))
    next_idx = 2
    next_button = None
    for elt_button in elts_buttons:
        if elt_button.text == str(next_idx):
            next_button = elt_button
            break
    while len(texts) < 500 and next_button is not None:
        text_reviews = list()
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", next_button)
        next_idx += 1
        if driver.current_url not in checked_urls:
            checked_urls.append(driver.current_url)
            time.sleep(0.3)
            elts_reviews = driver.find_elements_by_class_name(
                "lemon--p__373c0__3Qnnj.text__373c0__2Kxyz.comment__373c0__3EKjH.text-color--normal__373c0__3xep9.text-align--left__373c0__2XGa-")
            try:
                for elt in elts_reviews:
                    if elt.text not in text_reviews and elt.text not in texts:
                        text_reviews.append(elt.text)
            except exceptions.StaleElementReferenceException:
                pass
            texts.extend(text_reviews)
        try:
            time.sleep(0.3)
            elts_buttons = driver.find_elements_by_class_name(
                "lemon--div__373c0__1mboc.pagination-link--current__373c0__7SZSt.display--inline-block__373c0__1ZKqC border-color--default__373c0__3-ifU")
            next_button = None
            for elt_button in elts_buttons:
                if elt_button.text == str(next_idx):
                    next_button = elt_button
                    break
        except exceptions.StaleElementReferenceException:
            pass
    driver.quit()
    return texts


def getWebsiteDescription(url):
    text = ""
    chrome_driver = os.getcwd() + "/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    driver.get(url)
    elts = driver.find_elements_by_tag_name("p")
    for elt in elts:
        text += " " + elt.text
    driver.quit()
    return text


##################
# Routing utils
##################

def buildRoute(start, sights, foods, google_api_key):
    query = "https://maps.googleapis.com/maps/api/directions/json?origin=" + start \
              + "&destination="+start+"&waypoints=optimize:true|"
    for sight in sights:
        address = sight[2]
        query = query + address + "|"
    if foods is not None:
        for food in foods:
            address = food[2]
            query = query+address+"|"
    query = query + "&key=" + google_api_key
    rsp = requests.get(query).json()
    return rsp["routes"][0]["waypoint_order"]


##################
# Vision utils
##################

def identifySight(api_key, img):
    # use google cloud for vision library / google lens
    sight_name = None
    return sight_name
