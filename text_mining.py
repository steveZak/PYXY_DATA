import os
import json
import numpy as np
from text_mining_utils import getCityName, gatherPlaceData, getText, getProfiles, getTripText, getWebsiteDescription, getYelpText, getGoogleReviews, getGooglePopularity, getWebsite


def main(city_dir_name, data_type='sights', google_api_key="AIzaSyB1z27ziPvK-fJFinlz_gzgPbPt4XR55Bk"):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "CLOUD_ACCESS/creds.json"
    city = getCityName(city_dir_name)
    # get google maps place data
    sights_text = list()
    sights_profile = list()
    places = gatherPlaceData(api_key=google_api_key, data_type=data_type, city=city)
    print("Found " + str(len(places)) + " places")
    with open("CITY_DATABASES/" + city_dir_name + "/text.json", 'w') as file:
        with open("CITY_DATABASES/" + city_dir_name + "/profiles.json", 'w') as file_p:
            for place in places:
                print(place['name'])
                name_check = place['name'].lower()
                if 'visitor' in name_check or 'tourist' in name_check or ' tours' in name_check\
                        or 'hotel' in name_check or ' inn ' in name_check or 'hostel' in name_check\
                        or name_check == city.lower():
                    continue
                sights_profile.append(getProfiles(place, city, google_api_key))
                sights_text.append(getText(place, city, sights_profile[-1]['website']))
            json.dump({"sights": sights_text}, file, indent=2)
            json.dump({"sights": sights_profile}, file_p, indent=2)
    return


def addTextFile(city_dir_name, api_key="AIzaSyB1z27ziPvK-fJFinlz_gzgPbPt4XR55Bk"):
    city = getCityName(city_dir_name)
    with open("CITY_DATABASES/" + city_dir_name + "/profiles.json", 'r') as file_p:
        profiles = json.load(file_p)["sights"]
    sights_profiles = list()
    sights_text = list()
    for profile in profiles:
        print(profile['name'])
        if 'website' not in profile:
            profile['website'] = getWebsite(profile['place_id'], api_key)
        sights_text.append(getText(profile, city, profile['website']))
        sights_profiles.append(profile)
    with open("CITY_DATABASES/" + city_dir_name + "/text.json", 'w') as file:
        json.dump({"sights": sights_text}, file, indent=2)
    with open("CITY_DATABASES/" + city_dir_name + "/profiles.json", 'w') as file:
        json.dump({"sights": sights_profiles}, file, indent=2)
    return


def addTextElt(city_dir, text_field='trip'):
    # add trip text to a dir
    with open("CITY_DATABASES/" + city_dir + '/text.json', 'r') as file:
        data = json.load(file)
    data_new = {'sights': list()}
    for sight in data['sights']:
        if text_field == 'google':
            sight['text']['google'] = getGoogleReviews(sight['place_id'], city_dir)
            if 'reviews' in sight['text']:
                sight['text'].pop('reviews')
        if text_field == 'yelp':
            sight['text']['yelp'] = getYelpText(sight['name'], city_dir)
        if text_field == 'trip':
            sight['text']['trip'] = getTripText(sight['name'], city_dir)
        if text_field == 'website':
            for i in range(len(sight['text']['website'])):
                sight['text']['website'][i]['content'] = getWebsiteDescription(sight['text']['website'][i]['source'])
        data_new['sights'].append(sight)
        print(sight['name'])
    with open("CITY_DATABASES/" + city_dir + '/text.json', 'w') as file:
        json.dump(data_new, file, indent=2)


def addPopularityK(city_dir):
    # add trip text to a dir
    with open("CITY_DATABASES/" + city_dir + '/profiles.json', 'r') as file:
        data = json.load(file)
    if 'num_google_reviews' in data['sights'][0]:
        return
    data_new = {'sights': list()}
    high = 0
    for sight in data['sights']:
        print(sight['name'])
        pop = getGooglePopularity(sight['place_id'], city_dir)
        sight['popularity'] = pop
        data_new['sights'].append(sight)
        if pop > high:
            high = pop
    for i in range(len(data_new['sights'])):
        data_new['sights'][i]['num_google_reviews'] = data_new['sights'][i]['popularity']
        data_new['sights'][i]['popularity'] = np.sqrt(np.sqrt(float(data_new['sights'][i]['popularity']) / high))
    with open("CITY_DATABASES/" + city_dir + '/profiles.json', 'w') as file:
        json.dump(data_new, file, indent=2)
    return


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
    if 'google' not in data['sights'][0]['text'] or len(data['sights'][0]['text']['google']) < 8:
        return False
    return True


def isAnalyzeDone(dir):
    with open("CITY_DATABASES/" + dir + '/profiles.json') as file:
        data = json.load(file)['sights']
    if 'mood_params' in data[0]:
        return True
    return False


# def isPopularityDone(dir):
#     with open("CITY_DATABASES/" + dir + '/profiles.json') as file:
#         data = json.load(file)['sights']
#     if 'popularity' in data[0]:
#         return True
#     return False


# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for dir in dirs:
#         # print(dir)
#         if isMetadataGathered(dir):
#             if isTextMetadataFinal(dir):
#                 if not isTextFinal(dir):
#                     print(dir)
#                     print("will gather long text data")
#                     addTextElt(dir, 'google')
#                     continue
#                 print(dir)
#                 print("Long text data gathered")
#                 continue
#             # print(dir)
#             # print("Formatting text file")
#             # addTextFile(dir)
#         # print("Gathering profile metadata")
#         # main(dir)

# for _, dirs, _ in os.walk(os.getcwd() + "/CITY_DATABASES"):
#     for dir in dirs:
#         if isMetadataGathered(dir):
#             if isTextMetadataFinal(dir):
#                 if isTextFinal(dir):
#                     print(dir)
#                     addPopularityK(dir)


# addTextElt("CHENNAI_TA_IN", 'trip')
# addTextElt("ALGIERS_AL_DZ", 'trip')
# addTextElt("BATH_EN_GB", 'trip')
# addTextElt("BLACKPOOL_EN_GB", 'trip')
# addTextElt("BRIGHTON_EN_GB", 'trip')
# addTextElt("CAMBRIDGE_EN_GB", 'trip')
# addTextElt("ACAPULCO_GU_MX", 'trip')
# addTextElt("BAKU_BA_AZ", 'trip')
# addTextElt("CARACAS_CD_VE", 'trip')
# addTextElt("CHONGQING_CQ_CN", 'trip')
# addTextElt("COLUMBIA_SC_US", 'trip')
# addTextElt("CUSCO_CU_PE", 'trip')
# addTextElt("TIJUANA_BC_MX", 'trip')
# addTextElt("YELLOWKNIFE_NT_CA", 'trip')
# addTextElt("DES_MOINES_IA_US", 'trip')

# addTextElt("HANGZHOU_ZJ_CN", 'trip')
# addTextElt("HARBIN_HL_CN", 'trip')
# addTextElt("ISLAMABAD_CT_PK", 'trip')
# addTextElt("MADURAI_TA_IN", 'trip')
# addTextElt("MONTERREY_NL_MX", 'trip')
# addTextElt("NARA_KA_JP", 'trip')
# addTextElt("SACRAMENTO_CA_US", 'trip')
# addTextElt("MACAO_MA_CN", 'trip')
# addTextElt("OSAKA_KN_JP", 'trip')
# addTextElt("ST_PAUL_MN_US", 'trip')
# addTextElt("QINGDAO_SD_CN", 'trip')
# addTextElt("SAPPORO_HO_JP", 'trip')
# addTextElt("LILLE_HF_FR", 'trip')
# addTextElt("KINGSTON_SU_JM", 'trip')
# addTextElt('ALEXANDRIA_AL_EG', 'trip')

# addTextElt("BAGHDAD_BA_IQ", 'trip')
# addTextElt("CANCUN_YU_MX", 'trip')
# addTextElt("CASABLANCA_CA_MA", 'trip')
# addTextElt("CHISINAU_CH_MD", 'trip')
# addTextElt("CORK_CO_IE", 'trip')
# addTextElt("GALWAY_GA_IE", 'trip')
# addTextElt("HAKONE_KN_JP", 'trip')
# addTextElt("HYDERABAD_AP_IN", 'trip')
# addTextElt("INCHEON_SE_KR", 'trip')
# addTextElt("LIMERICK_LI_IE", 'trip')
# addTextElt("MECCA_MA_SA", 'trip')
# addTextElt("MEDINA_AM_SA", 'trip')
# addTextElt("MERIDA_YU_MX", 'trip')
# addTextElt("PYONGYANG_PY_KP", 'trip')
# addTextElt("OMAHA_NE_US", 'trip')
# addTextElt("TULSA_OK_US", 'trip')
# addTextElt("WICHITA_KS_US", 'trip')
# addTextElt("SEVILLE_AN_ES", 'trip')
# addTextElt("TASHKENT_TA_UZ", 'trip')
# addTextElt("TEL_AVIV_GD_IL", 'trip')

# main("ZARAGOZA_AR_ES")
# main("YOKOHAMA_KN_JP")
# main("XINING_QH_CN")
# main("XIAN_SA_CN")

# main("TURKU_SF_FI")
# main("TUNIS_TU_TN")
# main("TRONDHEIM_TR_NO")
# main("TBILISI_TB_GE")
# main("STRAVANGER_RO_NO")
# main("SANTO_DOMINGO_ND_DO")
# main("RIYADH_RI_SA")
# main("PORT_AU_PRINCE_OU_HT")
# main("PHUKET_PH_TH")
# main("PALMA_BA_ES")
# main("HO_CHI_MINH_CITY_SE_VN")
# main("HERAKLION_CR_GR")
# main("GEORGE_TOWN_PE_MY")
