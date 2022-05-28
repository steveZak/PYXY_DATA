import numpy as np
import random
import json
from geopy import distance
# from create_city_trips import isMetadataGathered, isTextMetadataFinal, isTextFinal, isAnalyzeDone

########################
#  Coordinate utils
########################


def buildBasicTrips(city_dir):
    themes_names = ["Amusement",
                    "Animals",
                    "Architecture",
                    "Art",
                    "Beach",
                    "Books",
                    "Cosmopolitan",
                    "Culture",
                    "Engineering",
                    "Family",
                    "Fashion",
                    "Food",
                    "Friends",
                    "Hiking",
                    "History",
                    "Hospitality",
                    "Insta",
                    "Military",
                    "Music",
                    "Movies",
                    "Nature",
                    "Nightlife",
                    "Original",
                    "Religion",
                    "Science",
                    "Shopping",
                    "Sport",
                    "Views",
                    "Walking",
                    "Water"]
    moods_names = ["Adventuresome",
                   "Entertaining",
                   "Peaceful",
                   "Captivating",
                   "Magical",
                   "Exciting",
                   "Impressive",
                   "Inspiring",
                   "Romantic",
                   "Scary",
                   "Wise",
                   "Sad"]
    with open("CITY_DATABASES/" + city_dir + "/profiles.json") as file:
        all_sights = json.load(file)['sights']
    for i in range(len(all_sights)):
        all_sights[i].pop('cat_params')
        if 'noncat_params' in all_sights[i]:
            all_sights[i].pop('noncat_params')
        all_sights[i].pop('mood_params')
        all_sights[i].pop('photos')
        all_sights[i].pop('num_google_reviews')
        all_sights[i].pop('top_cats')
    num_params = len(all_sights[0]['global_cat_params'])
    themes = np.zeros(num_params)
    for sight in all_sights:
        themes += np.array(sight['global_cat_params'])
    top_themes = themes.argsort()[::-1]
    themed = []
    for idx in top_themes:
        sights = sorted(all_sights, key=lambda x: x['global_cat_params'][idx], reverse=True)  # switch
        steps = []
        for i in range(5, 9):
            steps.append(sights[i+1]['global_cat_params'][idx] - sights[i]['global_cat_params'][idx])
        end = steps.index(min(steps))
        sights = sights[:5+end + 1]
        route = buildRoute(sights)
        themed.append({"sights": route, "trip_id": city_dir + "_T_" + themes_names[idx].upper(),
                       "distance": getTotalRouteDist(route)})  # aggregate ratings and number saved in real db
    # moods
    num_params = len(all_sights[0]['global_mood_params'])
    moods = np.zeros(num_params)
    for sight in all_sights:
        moods += np.array(sight['global_mood_params'])
    top_moods = moods.argsort()[::-1]
    mooded = []
    for idx in top_moods:
        sights = sorted(all_sights, key=lambda x: x['global_mood_params'][idx], reverse=True)  # switch
        steps = []
        for i in range(5, 9):
            steps.append(sights[i+1]['global_mood_params'][idx] - sights[i]['global_mood_params'][idx])
        end = steps.index(min(steps))
        sights = sights[:5+end + 1]
        route = buildRoute(sights)
        mooded.append({"sights": route, "trip_id": city_dir + "_M_" + moods_names[idx].upper(),
                       "distance": getTotalRouteDist(route)})  # aggregate ratings and number saved in real db
    # popularity
    popped = []
    sights = sorted(all_sights, key=lambda x: x['popularity'], reverse=True)
    steps = []
    for i in range(5, 9):
        steps.append(sights[i + 1]['popularity'] - sights[i]['popularity'])
    end = steps.index(min(steps))
    sights = sights[:5+end + 1]
    route = buildRoute(sights)
    popped.append({"sights": route, "trip_id": city_dir + "_D_MUST_GOS", "distance": getTotalRouteDist(route)})  # aggregate ratings and number saved in real db
    sights = sorted(all_sights, key=lambda x: x['popularity'])
    random.shuffle(sights[:20])
    sights = sights[:random.randint(5, 9)]
    route = buildRoute(sights)
    popped.append(
        {"sights": route, "trip_id": city_dir + "_D_RARE_SPOTS", "distance": getTotalRouteDist(route)})  # aggregate ratings and number saved in real db
    # distance
    disted = []
    sights = all_sights.copy()
    random.shuffle(sights)
    sights = sights[:random.randint(9, 11)]
    route = buildRoute(sights)
    disted.append({"sights": route, "trip_id": city_dir+"_D_MARATHON",
                   "distance": getTotalRouteDist(route)})  # aggregate ratings and number saved in real db
    sights = all_sights.copy()
    random.shuffle(sights)
    sights = sights[:random.randint(4, 6)]
    route = buildRoute(sights)
    disted.append(
        {"sights": route, "trip_id": city_dir+"_D_GETAWAY",
         "distance": getTotalRouteDist(route)})  # aggregate ratings and number saved in real db
    trips = dict()
    trips["theme_trips"] = addTripParams(themed)
    trips["mood_trips"] = addTripParams(mooded)
    trips["popularity_trips"] = addTripParams(popped)
    trips["distance_trips"] = addTripParams(disted)
    return trips


def buildCityConfig(city_dir):
    with open("CITY_DATABASES/" + city_dir + "/profiles.json") as file:
        sights = json.load(file)['sights']
    cat_params, mood_params = [], []
    for sight in sights:
        if len(cat_params) == 0:
            cat_params = sight['global_cat_params']
            mood_params = sight['global_mood_params']
        else:
            cat_params = [a+b for a, b in zip(cat_params, sight['global_cat_params'])]
            mood_params = [a+b for a, b in zip(mood_params, sight['global_mood_params'])]
    cat_params = [a/(len(sights)*np.sqrt(sum([(1.0/len(sights))**2 for i in sights]))) for a in cat_params]
    mood_params = [a/(len(sights)*np.sqrt(sum([(1.0/len(sights))**2 for i in sights]))) for a in mood_params]
    return {"cat_params": cat_params, "mood_params": mood_params}  # adjust z scores for trips


# def addHours(city_dir):
#     with open


def addTripParams(trips):
    for i in range(len(trips)):
        cats = np.zeros(len(trips[i]['sights'][0]['global_cat_params']))
        moods = np.zeros(len(trips[i]['sights'][0]['global_mood_params']))
        pop = 0
        for sight in trips[i]['sights']:
            cats += sight['global_cat_params']
            moods += sight['global_mood_params']
            pop += sight['popularity']
        denom = np.sqrt(sum([(1.0 / len(trips[i]['sights'])) ** 2 for j in range(len(trips[i]['sights']))]))
        trips[i]['global_cat_params'] = (cats/(len(trips[i]['sights'])*denom)).tolist()
        trips[i]['global_mood_params'] = (moods/(len(trips[i]['sights'])*denom)).tolist()
        trips[i]['pop'] = pop/len(trips[i]['sights'])
    return trips


########################
#  Coordinate utils
########################


def convertCoordinates(coords):
    return str(coords['lat']) + ', ' + str(coords['lng'])


def getDistanceFromCoordinates(c1, c2):
    return distance.distance(c1, c2).km


def getTotalRouteDist(sights):
    total = 0
    for i in range(len(sights)-1):
        total += getDistanceFromCoordinates(convertCoordinates(sights[i]['coordinates']),
                                            convertCoordinates(sights[i+1]['coordinates']))
    return total


########################
#  Routing utils
########################


def buildRoute(locs, foods=False, pop_size=35, elite_size=8, mut_rate=0.01, gens=100):
    if len(locs) > 10:
        pop_size = 45
        gens = 100
    if not foods:
        pop = [random.sample(locs, len(locs)) for i in range(pop_size)]
        for i in range(gens):
            pop = nextGen(pop, elite_size, mut_rate)
        return pop[0]
    return


def nextGen(curr_gen, elite_size, mut_rate):
    pop_sorted = rankRoutes(curr_gen)
    selected_pop = selection(pop_sorted, elite_size)
    children = breedPop(selected_pop, elite_size)
    new_pop = mutate(children, mut_rate)
    return new_pop


def selection(pop, elite_size):
    pop[:elite_size].extend(random.sample(pop, len(pop) - elite_size))
    return pop


def mutate(pop, mut_rate):
    for i in range(len(pop)):
        for swapped in range(len(pop[i])):
            if random.random() < mut_rate:
                swap_with = int(random.random() * len(pop[i]))
                tmp = pop[i][swap_with]
                pop[i][swap_with] = pop[i][swapped]
                pop[i][swapped] = tmp
    return pop


def breedPop(mating_pool, elite_size):
    children = []
    length = len(mating_pool) - elite_size
    pool = random.sample(mating_pool, len(mating_pool))
    for i in range(elite_size):
        children.append(mating_pool[i])
    for i in range(length):
        child = breed(pool[i], pool[len(mating_pool)-i-1])
        children.append(child)
    return children


def breed(parent1, parent2):
    child_1 = []
    gene_a = int(random.random()*len(parent1))
    gene_b = int(random.random()*len(parent1))
    start_gene = min(gene_a, gene_b)
    end_gene = max(gene_a, gene_b)
    for i in range(start_gene, end_gene):
        child_1.append(parent1[i])
    child_2 = [item for item in parent2 if item not in child_1]
    child = child_1 + child_2
    return child


def rankRoutes(pop):
    fitnesses = list()
    for i in range(len(pop)):
        fitness = 0
        for j in range(len(pop[0]) - 1):
            fitness += getDistanceFromCoordinates(convertCoordinates(pop[i][j]["coordinates"]),
                                                  convertCoordinates(pop[i][j+1]["coordinates"]))
        fitnesses.append(fitness)
    return [x for _, x in sorted(zip(fitnesses, pop), key=lambda x: x[0])]
