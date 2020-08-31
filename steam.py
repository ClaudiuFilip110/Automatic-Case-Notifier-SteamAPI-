import requests
import pandas as pd
import time
import pickle
import os
from pprint import pprint

# not permanent but I can't find a way to automatically retrieve a list of all the cases
data = ['Chroma 2 Case', 'Chroma 3 Case', 'Chroma Case', 'Clutch Case', 'CS:GO Weapon Case',
        'CS:GO Weapon Case 2', 'CS:GO Weapon Case 3', 'CS20 Case', 'Danger Zone Case', 'eSports 2013 Case',
        'eSports 2013 Winter Case', 'eSports 2014 Summer Case', 'Falchion Case', 'Fracture Case', 'Gamma 2 Case', 'Gamma Case',
        'Glove Case', 'Horizon Case', 'Huntsman Weapon Case', 'Operation Bravo Case', 'Operation Breakout Weapon Case',
        'Operation Hydra Case', 'Operation Phoenix Weapon Case', 'Operation Vanguard Weapon Case', 'Operation Wildfire Case', 'Prisma 2 Case',
        'Prisma Case', 'Revolver Case', 'Shadow Case', 'Shattered Web Case', 'Spectrum 2 Case', 'Spectrum Case',
        'Winter Offensive Weapon Case']

users = ['uraniumiscute', 'seven_hack69', 'ClaudiuFilip110']
req = 'https://steamcommunity.com/id/' + users[1] + '/inventory/json/730/2'
try:
    r = requests.get(req)
except:
    print("Status code:", r.status_code)
    print("bad request OR server unavailable")
    quit()
theJSON = r.json()

# nothing important, it's meaningless
nothing = True

inventory = theJSON["rgInventory"]
descriptions = theJSON["rgDescriptions"]
# initialize the DICT with the available cases
Cases = {}
for key in descriptions:
    item = descriptions[key]
    if " Case" in item["name"]:
        _case = item["name"]
        Cases[_case] = 0
# get number of cases in dict
for key in descriptions:
    item = descriptions[key]
    if " Case" in item["name"]:
        for invent in inventory:
            x = inventory[invent]
            if item["classid"] == x["classid"]:
                Cases[item["name"]] += 1

PICKLE_MARKET = []
STEAM_MARKET = []
# -----------pickle module
print('Do you want to compare the market prices with your stored prices? (Y / N) ', end='')
market_refresh = str(input())
market_refresh = market_refresh.upper()
pickle_in = open("current_market.pickle", "rb")
PICKLE_MARKET = pickle.load(pickle_in)
if market_refresh != 'Y':
    nothing = True
else:
    for i in range(len(data)):
        case = data[i]
        before_replace = case
        case = case.replace(' ', '%20').replace(':', '%3A')
        req = 'https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=' + case
        # wait 3 seconds because the server doesn't allow more than 20 queries/ min.
        time.sleep(3)
        r = requests.post(req)
        # convert the price from string to float
        #price = r.json()['lowest_price'].replace(',','.').replace('€','')
        STEAM_MARKET.append(r.json()['lowest_price'])
        # print('loading...')
        print(before_replace, r.json()['lowest_price'],
              'Response from server:', str(r.status_code))
        # with open("current_market.pickle", "wb") as f:
        #     pickle.dump(STEAM_MARKET, f)

# CASES
cases = data

# QTY of cases
QTY = [0 for i in range(len(cases))]
for key in descriptions:
    item = descriptions[key]
    if " Case" in item["name"]:
        if item["name"] in cases:
            # add qty at the right index
            QTY[cases.index(item["name"])] = Cases[item["name"]]

# MARKET
MARKET_CUT = []
float_market = []
float_market_rounded = [0 for i in range(len(QTY))]

for i in PICKLE_MARKET:
    float_market.append(
        float(i.replace('€', '').replace(',', '.').replace('--', '00')))
for i in range(len(float_market)):
    float_market_rounded[i] = round(float_market[i]/1.149-0.01, 2)

# TOTAL
TOTAL = [0 for i in range(len(cases))]
for i in range(len(QTY)):
    TOTAL[i] = QTY[i] * float_market[i]

# TOTAL w~ CUT
TOTAL_CUT = [0 for i in range(len(cases))]
for i in range(len(QTY)):
    TOTAL_CUT[i] = QTY[i] * float_market_rounded[i]
pickle_data = {
    'CASES': cases,
    'QTY': QTY,
    'MARKET': float_market,
    'MARKET w~ CUT': float_market_rounded,
    'TOTAL': TOTAL,
    'TOTAL w~ CUT': TOTAL_CUT,
}
pickle = pd.DataFrame(data=pickle_data)
if market_refresh != 'Y':
    print('These are the last stored prices')
print(pickle)

float_steam = []
for price in STEAM_MARKET:
    float_steam.append(
        float(price.replace('€', '').replace(',', '.').replace('--', '00')))
steam_data = {
    'CASES': cases,
    'STEAM': float_steam
}
steam = pd.DataFrame(data=steam_data)

if(STEAM_MARKET):
    print(steam)
else:
    print("steam prices not available")

steam_market_series = [0 for i in range(len(cases))]
for i in range(len(STEAM_MARKET)):
    steam_market_series[i] = str(STEAM_MARKET[i]) + '€'

compare_data = {
    'CASES': cases,
    'PICKLE': PICKLE_MARKET,
    'MARKET': STEAM_MARKET,
    'DIFF': pickle['MARKET'] - steam['STEAM']
}
compare = pd.DataFrame(data=compare_data)
print(compare)