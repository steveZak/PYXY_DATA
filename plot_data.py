import matplotlib.pyplot as plt
import json
import os
import numpy as np

plt.rc('font', size=6)
city_dir = "CHICAGO_IL_US"

cat1 = 'history'
cat2 = 'nightlife'

with open(os.getcwd() + "/CITY_DATABASES/" + city_dir + '/params.json', mode='r') as file:
    data = json.load(file)
    categories = data['categories']
    idx1 = categories.index(cat1)
    idx2 = categories.index(cat2)
    sights = data['sights']
    for sight in sights:
        if sight['cat_params'][idx1] != 0 or sight['cat_params'][idx2] != 0:
            plt.plot(sight['cat_params'][idx1], sight['cat_params'][idx2], 'ro')
            plt.annotate("  " + sight['name'], (sight['cat_params'][idx1], sight['cat_params'][idx2]))

plt.xlabel(cat1)
plt.ylabel(cat2)
plt.title(cat1 + " and " + cat2 + " category scores for sights in " + city_dir)
plt.savefig("plot.png")
