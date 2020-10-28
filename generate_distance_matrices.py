import os
import json
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main(city_dir):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver = os.getcwd() + "/chromedriver"
    # driver = webdriver.Chrome(executable_path=chrome_driver)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    with open(os.getcwd()+"/CITY_DATABASES/"+city_dir+"/profiles.json") as file:
        sights = json.load(file)['sights']
    cities = []
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
                # print(sights[i]['name'])
                # print(sights[j]['name'])
                url = "https://www.google.com/maps/dir/"+str(sights[i]['coordinates']['lat'])+","+str(sights[i]['coordinates']['lng'])+"/"\
                                                        +str(sights[j]['coordinates']['lat'])+","+str(sights[j]['coordinates']['lng'])+"/"
                driver.get(url) # gets recommended, specify driving, cycling, walking
                btns = driver.find_elements_by_class_name("travel-mode")
                time.sleep(1)
                btns[1].click()
                time.sleep(2)
            if j>i: # driving
                time_elts = driver.find_elements_by_class_name("section-directions-trip-duration")
                if len(time_elts) > 0:
                    time_txt = time_elts[0].text
                    elts = driver.find_elements_by_class_name("section-directions-trip-distance")
                    if len(elts) > 0:
                        dist_txt = elts[0].text
                        drive_dist_matrix[i][j] = 1.60934*float(dist_txt.split(' ')[0]) if 'mi' in dist_txt else float(dist_txt.split(' ')[0])
                    if 'h' in time_txt:
                        if 'm' not in time_txt:
                            drive_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                        else:
                            drive_time_matrix[i][j] = 60*int(time_txt.split('h')[0]) + int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                    else:
                        drive_time_matrix[i][j] = int(time_txt.split('min')[0])
                else:
                    drive_dist_matrix[i][j] = np.NaN
                    drive_time_matrix[i][j] = np.NaN
                # print(drive_dist_matrix)
                # print(drive_time_matrix)
            else:
                drive_dist_matrix[i][j] = drive_dist_matrix[j][i]
                drive_time_matrix[i][j] = drive_time_matrix[j][i]
            if j>i:
                btns[2].click()
                time.sleep(2)
            if j>i: # transit
                time_elts = driver.find_elements_by_class_name("section-directions-trip-duration")
                if len(time_elts)>0:
                    time_txt = time_elts[0].text
                    elts = driver.find_elements_by_class_name("section-directions-trip-walking-duration")
                    if len(elts)> 0:
                        if 'min' in elts[0].text:
                            dist_txt = int(elts[0].text.split('min')[0])
                            transit_dist_walk_matrix[i][j] = 0.08333*dist_txt
                    if 'h' in time_txt:
                        if 'm' not in time_txt:
                            transit_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                        else:
                            transit_time_matrix[i][j] = 60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                    else:
                        transit_time_matrix[i][j] = int(time_txt.split('min')[0])
                # print(transit_dist_walk_matrix)
                # print(transit_time_matrix)
                else:
                    transit_dist_walk_matrix[i][j] = np.NaN
                    transit_time_matrix[i][j] = np.NaN
            else:
                transit_dist_walk_matrix[i][j] = transit_dist_walk_matrix[j][i]
                transit_time_matrix[i][j] = transit_time_matrix[j][i]
            if j>i:
                btns[3].click()
                time.sleep(2)
            if j>i: # walking
                time_elts = driver.find_elements_by_class_name("section-directions-trip-duration")
                if len(time_elts)>0:
                    time_txt = time_elts[0].text
                    dist_elts = driver.find_elements_by_class_name("section-directions-trip-distance.section-directions-trip-secondary-text")
                    if len(dist_elts)> 0: # get distance
                        dist_txt = dist_elts[0].text
                        walk_dist_matrix[i][j] = 1.60934*float(dist_elts[0].text.split(' ')[0]) if 'mi' in dist_txt else float(dist_txt.split(' ')[0])
                    else: # infer from time
                        if 'h' in time_txt:
                            if 'm' not in time_txt:
                                walk_dist_matrix[i][j] = 0.08333*(60*int(time_txt.split('h')[0]))
                            else:    
                                walk_dist_matrix[i][j] = 0.08333*(60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1]))
                        else:
                            walk_dist_matrix[i][j] = 0.08333*(int(time_txt.split('min')[0]))
                    if 'h' in time_txt:
                        if 'm' not in time_txt:
                            walk_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                        else:
                            walk_time_matrix[i][j] = 60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                    else:
                        walk_time_matrix[i][j] = int(time_txt.split('min')[0])
                else:
                    walk_dist_matrix[i][j] = np.NaN
                    walk_time_matrix[i][j] = np.NaN
            else:
                walk_dist_matrix[i][j] = walk_dist_matrix[j][i]
                walk_time_matrix[i][j] = walk_time_matrix[j][i]
            if j>i:
                btns[4].click()
                time.sleep(2)
            if j>i: # cycling
                time_elts = driver.find_elements_by_class_name("section-directions-trip-duration")
                if len(time_elts)>0:
                    time_txt = time_elts[0].text
                    elts = driver.find_elements_by_class_name("section-directions-trip-distance")
                    if len(elts) > 0:
                        dist_txt = elts[0].text
                        cycle_dist_matrix[i][j] = 1.60934*float(dist_txt.split(' ')[0]) if 'mi' in dist_txt else float(dist_txt.split(' ')[0])
                    if 'h' in time_txt:
                        if 'm' not in time_txt:
                            cycle_time_matrix[i][j] = 60*int(time_txt.split('h')[0])
                        else:
                            cycle_time_matrix[i][j] = 60*int(time_txt.split('h')[0])+int(time_txt.split('h')[1].split('min')[0].split(' ')[1])
                    else:
                        cycle_time_matrix[i][j] = int(time_txt.split('min')[0])
                else:
                    cycle_dist_matrix[i][j] = np.NaN
                    cycle_time_matrix[i][j] = np.NaN
                # print(cycle_dist_matrix)
                # print(cycle_time_matrix)
            else:
                cycle_dist_matrix[i][j] = cycle_dist_matrix[j][i]
                cycle_time_matrix[i][j] = cycle_time_matrix[j][i]
    with open(os.getcwd()+"/CITY_DATABASES/"+ city_dir +"/distance.json", 'w') as file:
        json.dump({"drive_dist_matrix": drive_dist_matrix.tolist(), "drive_time_matrix": drive_time_matrix.tolist(), "transit_dist_walk_matrix": transit_dist_walk_matrix.tolist(), "transit_time_matrix": transit_time_matrix.tolist(), "walk_dist_matrix": walk_dist_matrix.tolist(), "walk_time_matrix": walk_time_matrix.tolist(), "cycle_dist_matrix": cycle_dist_matrix.tolist(), "cycle_time_matrix": cycle_time_matrix.tolist()}, file, indent=2)

main("ZAGREB_ZA_HR")