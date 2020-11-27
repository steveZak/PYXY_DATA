import os
import json
import time
import math
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main(city_dir):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver = os.getcwd() + "/chromedriver"
    # driver = webdriver.Chrome(executable_path=chrome_driver)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    with open(os.getcwd()+"/CITY_DATABASES/"+city_dir+"/profiles.json") as file:
        sights = json.load(file)['sights']
    drive_dist_matrix = np.zeros((len(sights), len(sights)))
    drive_time_matrix = np.zeros((len(sights), len(sights)))
    transit_dist_walk_matrix = np.zeros((len(sights), len(sights)))
    transit_time_matrix = np.zeros((len(sights), len(sights)))
    walk_dist_matrix = np.zeros((len(sights), len(sights)))
    walk_time_matrix = np.zeros((len(sights), len(sights)))
    cycle_dist_matrix = np.zeros((len(sights), len(sights)))
    cycle_time_matrix = np.zeros((len(sights), len(sights)))
    for i in range(len(sights)):
        print(sights[i]['name'])
        for j in range(len(sights)):
            if j>i:
                # print(sights[j]['name'])
                url = "https://www.google.com/maps/dir/"+str(sights[i]['coordinates']['lat'])+","+str(sights[i]['coordinates']['lng'])+"/"\
                                                        +str(sights[j]['coordinates']['lat'])+","+str(sights[j]['coordinates']['lng'])+"/"
                driver.get(url) # gets recommended, specify driving, cycling, walking
                # time.sleep(1)
                try:
                    btns = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "travel-mode")))
                    btns = driver.find_elements_by_class_name("travel-mode")
                finally:
                    btns[1].click()
                    time_txt, dist_txt = None, None
                # btns = driver.find_elements_by_class_name("travel-mode")
                # btns[1].click()
                # time.sleep(1.4)
            if j>i: # driving
                for k in range(4):
                    try:
                        time_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-duration"))).text
                        dist_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-distance"))).text
                    except:
                        pass
                    if time_txt is not None and dist_txt is not None:
                        if time_txt == '':
                            drive_dist_matrix[i][j] = np.NaN
                            drive_time_matrix[i][j] = np.NaN
                            break
                        if 'd' in time_txt:
                            drive_time_matrix[i][j] = np.NaN
                            drive_dist_matrix[i][j] = np.NaN
                            break
                        if 'mi' in dist_txt:
                            drive_dist_matrix[i][j] = 1.60934*float(dist_txt.split(' ')[0])
                        elif 'km' in dist_txt:
                            drive_dist_matrix[i][j] = float(dist_txt.split(' ')[0])
                        else:
                            drive_dist_matrix[i][j] = float(dist_txt.split(' ')[0])/1000.0
                        if 'h' in time_txt:
                            if 'm' not in time_txt:
                                drive_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                            else:
                                drive_time_matrix[i][j] = 60*int(time_txt.split('h')[0]) + int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                        else:
                            drive_time_matrix[i][j] = int(time_txt.split('min')[0])
                        break
                    drive_dist_matrix[i][j] = np.NaN
                    drive_time_matrix[i][j] = np.NaN
                # print('drive')
                # print(drive_dist_matrix[i][j])
                # print(drive_time_matrix[i][j])
            else:
                drive_dist_matrix[i][j] = drive_dist_matrix[j][i]
                drive_time_matrix[i][j] = drive_time_matrix[j][i]
            if j>i:
                btns[2].click()
                time_txt, dist_txt = None, None
            if j>i: # transit
                for k in range(4):
                    try:
                        time_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-duration"))).text
                        dist_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-walking-duration"))).text
                    except:
                        pass
                    if time_txt is not None and dist_txt is not None:
                        if time_txt == '':
                            transit_time_matrix[i][j] = np.NaN
                            break
                        if dist_txt == '':
                            transit_dist_walk_matrix[i][j] = np.NaN
                            break
                        if 'h' in dist_txt:
                            if 'min' in dist_txt:
                                dist_txt = 60*int(dist_txt.split('h')[0])+int(dist_txt.split('h')[1].split('min')[0].split(' ')[1])
                            else:
                                dist_txt = 60*int(dist_txt.split('h')[0])
                        else:
                            dist_txt = int(dist_txt.split('min')[0])
                        transit_dist_walk_matrix[i][j] = 0.08333*dist_txt
                        if 'h' in time_txt:
                            if 'm' not in time_txt:
                                if 'day' in time_txt:
                                    transit_time_matrix[i][j] = np.NaN
                                else:
                                    transit_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                            else:
                                transit_time_matrix[i][j] = 60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                        else:
                            if len(time_txt.split('min')[0]) > 0:
                                transit_time_matrix[i][j] = int(time_txt.split('min')[0])
                        break
                    transit_dist_walk_matrix[i][j] = np.NaN
                    transit_time_matrix[i][j] = np.NaN
                # print('transit')
                # print(transit_dist_walk_matrix[i][j])
                # print(transit_time_matrix[i][j])
            else:
                transit_dist_walk_matrix[i][j] = transit_dist_walk_matrix[j][i]
                transit_time_matrix[i][j] = transit_time_matrix[j][i]
            if j>i:
                btns[3].click()
                time_txt, dist_txt = None, None
            if j>i: # walking
                time_txt = None
                for k in range(4):
                    try:
                        time_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-duration"))).text
                        dist_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-distance"))).text
                    except:
                        pass
                    if time_txt is not None and dist_txt is not None:
                        if time_txt == '':
                            walk_time_matrix[i][j] = np.NaN
                            break
                        if dist_txt == '':
                            walk_dist_matrix[i][j] = np.NaN
                            break
                        if 'd' in time_txt:
                            walk_time_matrix[i][j] = np.NaN
                            walk_dist_matrix[i][j] = np.NaN
                            break
                        if 'mi' in dist_txt:
                            walk_dist_matrix[i][j] = 1.60934*float(dist_txt.split(' ')[0])
                        elif 'km' in dist_txt:
                            walk_dist_matrix[i][j] = float(dist_txt.split(' ')[0])
                        else:
                            walk_dist_matrix[i][j] = float(dist_txt.split(' ')[0])/1000.0
                    # else: # infer from time
                    #     if 'h' in time_txt:
                    #         if 'm' not in time_txt:
                    #             walk_dist_matrix[i][j] = 0.08333*(60*int(time_txt.split('h')[0]))
                    #         else:    
                    #             walk_dist_matrix[i][j] = 0.08333*(60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1]))
                    #     else:
                    #         walk_dist_matrix[i][j] = 0.08333*(int(time_txt.split('min')[0]))
                        if 'h' in time_txt:
                            if 'm' not in time_txt:
                                walk_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                            else:
                                walk_time_matrix[i][j] = 60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                        else:
                            walk_time_matrix[i][j] = int(time_txt.split('min')[0])
                        break
                    walk_dist_matrix[i][j] = np.NaN
                    walk_time_matrix[i][j] = np.NaN
                # print('walk')
                # print(walk_dist_matrix[i][j])
                # print(walk_time_matrix[i][j])
            else:
                walk_dist_matrix[i][j] = walk_dist_matrix[j][i]
                walk_time_matrix[i][j] = walk_time_matrix[j][i]
            if j>i:
                btns[4].click()
                time_txt, dist_txt = None, None
            if j>i: # cycling
                for k in range(4):
                    try:
                        time_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-duration"))).text
                        dist_txt = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "section-directions-trip-distance"))).text
                    except:
                        pass
                    if time_txt is not None and dist_txt is not None:
                        if time_txt == '':
                            cycle_dist_matrix[i][j] = np.NaN
                            cycle_time_matrix[i][j] = np.NaN
                            break
                        if 'mi' in dist_txt:
                            cycle_dist_matrix[i][j] = 1.60934*float(dist_txt.split(' ')[0])
                        elif 'km' in dist_txt:
                            cycle_dist_matrix[i][j] = float(dist_txt.split(' ')[0])
                        else:
                            cycle_dist_matrix[i][j] = float(dist_txt.split(' ')[0])/1000.0
                        if 'h' in time_txt:
                            if 'm' not in time_txt:
                                cycle_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                            else:
                                cycle_time_matrix[i][j] = 60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                        else:
                            cycle_time_matrix[i][j] = int(time_txt.split('min')[0])
                        break
                    cycle_dist_matrix[i][j] = np.NaN
                    cycle_time_matrix[i][j] = np.NaN
                # print('cycle')
                # print(walk_dist_matrix[i][j])
                # print(walk_time_matrix[i][j])
            else:
                cycle_dist_matrix[i][j] = cycle_dist_matrix[j][i]
                cycle_time_matrix[i][j] = cycle_time_matrix[j][i]
    # with open(os.getcwd()+"/CITY_DATABASES/"+ city_dir +"/distance.json") as file:
    #     info = json.load(file)
    # info['cycle_dist_matrix'] = cycle_dist_matrix.tolist()
    # info['cycle_time_matrix'] = cycle_time_matrix.tolist()
    # with open(os.getcwd()+"/CITY_DATABASES/"+ city_dir +"/distance.json", 'w') as file:
    #     json.dump(info, file, indent=2)
    with open(os.getcwd()+"/CITY_DATABASES/"+ city_dir +"/distance.json", 'w') as file:
        json.dump({"drive_dist_matrix": drive_dist_matrix.tolist(), "drive_time_matrix": drive_time_matrix.tolist(), "transit_dist_walk_matrix": transit_dist_walk_matrix.tolist(), "transit_time_matrix": transit_time_matrix.tolist(), "walk_dist_matrix": walk_dist_matrix.tolist(), "walk_time_matrix": walk_time_matrix.tolist(), "cycle_dist_matrix": cycle_dist_matrix.tolist(), "cycle_time_matrix": cycle_time_matrix.tolist()}, file, indent=2)
    driver.quit()

def add_avg_distance():
    for _, dirs, _ in os.walk(os.getcwd()+"/CITY_DATABASES"):
        for city_dir in dirs:
            print(city_dir)
            if os.path.exists(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/distance.json"):
                with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/distance.json") as file:
                    data = json.load(file)
                driving_distance = data['drive_dist_matrix']
                avg_dd = 0
                cnt = 0
                for i in range(len(driving_distance)):
                    for j in range(len(driving_distance[i])):
                        if not math.isnan(driving_distance[i][j]):
                            cnt += 1
                            avg_dd += driving_distance[i][j]
                data['avg_dd'] = [[avg_dd/cnt]]
            with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + "/distance.json", 'w') as file:
                json.dump(data, file, indent=2)

# main("PHILADELPHIA_PA_US")
# main("ZAGREB_ZA_HR")
# main("ABUJA_CT_NI")
# main("ADELAIDE_SA_AU")
# main("AGRA_UP_IN")
# main("NEW_YORK_CITY_NY_US")
# main("SEATTLE_WA_US")
# main("ATLANTA_GA_US")
# main("ZURICH_ZH_CH")
# main("MOSCOW_MW_RU")
# main("BOSTON_MA_US")
# main("PORTLAND_OR_US")
# main("ABU_DHABI_AB_AE")
# main("ACAPULCO_GU_MX")

# main("ADDIS_ABABA_AA_ET")
# main("ALBUQUERQUE_NM_US")
# main("ALEXANDRIA_AL_EG")
# main("ALGIERS_AL_DZ")
# main("AMSTERDAM_NH_NL")
# main("ANAHEIM_CA_US")
# main("ANCHORAGE_AK_US")
# main("ANTALYA_ME_TR")
# main("ANTWERP_FC_BE")
# main("ATHENS_AT_GR")
# main("AUCKLAND_NI_NZ")
# main("AUSTIN_TX_US")
# main("AVIGNON_AC_FR")
# main("ZHENGZHOU_HN_CN")
# main("ZARAGOZA_AR_ES")
# main("YOKOHAMA_KN_JP")
# main("YEREVAN_YE_AM")
# main("YELLOWKNIFE_NT_CA")
# main("YEKATERINBURG_SV_RU")
# main("XINING_QH_CN")
# main("XIAN_SA_CN")
# main("WUHAN_HB_CN") # fixed line 99
# main("WINNIPEG_MB_CA")
# main("WICHITA_KS_US")
# main("WELLINGTON_NI_NZ")
# main("WASHINGTON_DC_US")
# main("WARSAW_MA_PL")
# main("VOLGOGRAD_VL_RU")
# main("VLADIVOSTOK_PR_RU")
# main("VIRGINIA_BEACH_VA_US")
# main("VILNIUS_VI_LT")
# main("VIENNA_VI_AT")
# main("VENICE_VE_IT")
# main("VATICAN_VA_HS")
# main("VARNA_VA_BG")
# main("VANCOUVER_BC_CA")
# main("VALENCIA_VA_ES")
# main("UPPSALA_UP_SE")
# main("TYUMEN_TY_RU")
# main("TURKU_SF_FI")
# main("TURIN_PI_IT")
# main("TUNIS_TU_TN")
# main("TULSA_OK_US")
# main("TUCSON_AZ_US")
# main("TRONDHEIM_TR_NO")
# main("TROMSO_TF_NO")
# main("BAGHDAD_BA_IQ")
# main("BAKU_BA_AZ")
# main("BALI_BA_ID")
# main("BALTIMORE_MD_US")
# main("BANFF_AB_CA")
# main("BANGKOK_CT_TH")
# main("BARCELONA_CA_ES")

# main("BARI_AP_IT") # switched NaN assignments previously set to cycling
# main("BASEL_BS_CH")
# main("BATH_EN_GB")
# main("TOULOUSE_OC_FR")
# main("TORONTO_ON_CA")
# main("TOKYO_KA_JP")
# main("TIJUANA_BC_MX") # remove SD places?
# main("TIANJIN_TJ_CN")
# main("THESSALONIKI_MC_GR")
# main("THE_HAGUE_SH_NL")
# main("TEL_AVIV_GD_IL")
# main("TEHRAN_TE_IR")
# main("TBILISI_TB_GE")
# main("TASHKENT_TA_UZ")
# main("TAMPA_FL_US")
# main("TALLINN_HA_EE")
# main("TAIPEI_TP_TW")
# main("SYDNEY_SW_AU")
# main("SWANSEA_WA_GB")
# main("SUZHOU_JS_CN")
# main("STUTTGART_BW_DE")
# main("STRASBOURG_GE_FR")
# main("STOCKHOLM_ST_SE")
# main("STAVANGER_RO_NO")
# main("ST_PAUL_MN_US")
# main("ST_LOUIS_MO_US")
# main("SOUTHAMPTON_EN_GB")
# main("SOFIA_SO_BG")
# main("SOCHI_KR_RU")
# main("SKYE_SC_GB")
# main("SINGAPORE_SG_SG")
# main("SHENZHEN_GD_CN")
# main("SHANGHAI_SH_CN")
# main("SEVILLE_AN_ES")
# main("SEOUL_SE_KR")
# main("SAVANNAH_GA_US")
# main("SAPPORO_HO_JP")
# main("SAO_PAOLO_SP_BR")
# main("SANTO_DOMINGO_ND_DO")
# main("SANTIAGO_SA_CL")
# main("SAN_MARINO_SM_SM")
# main("SAN_JUAN_PR_US")
# main("SAN_JOSE_CA_US")
# main("SAN_FRANCISCO_CA_US")
# main("SAN_DIEGO_CA_US")
# main("SAN_ANTONIO_TX_US")
# main("SALZBURG_SA_AT")
# main("SALT_LAKE_CITY_UT_US")
# main("SAINT_PETERSBURG_SP_RU")
# main("SACRAMENTO_CA_US")
# main("ROVANIEMI_LA_FI")
# main("ROTTERDAM_SH_NL")
# main("ROSTOV_ON_DON_RO_RU")
# main("ROME_LA_IT")
# main("RIYADH_RI_SA")
# main("RIO_DE_JANEIRO_RJ_BR")
# main("RIGA_RI_LV")
# main("RICHMOND_VA_US")
# main("REYKJAVIK_CR_IS")
# main("RALEIGH_NC_US")
# main("QUEBEC_CITY_QC_CA")
# main("QINGDAO_SD_CN")
# main("PYONGYANG_PY_KP")
main("PROVIDENCE_RI_US")
main("PRETORIA_GA_ZA")
main("PRAGUE_PR_CZ")
main("POTSDAM_BR_DE")
main("PORTO_NO_PT")
main("PORT_ELIZABETH_EC_ZA")

# add_avg_distance()
