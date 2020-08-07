import requests
import pandas as pd
import time 
import pickle
import os
from pprint import pprint

#not permanent
data = ['Chroma 2 Case','Chroma 3 Case', 'Chroma Case','Clutch Case','CS:GO Weapon Case',
        'CS:GO Weapon Case 2','CS:GO Weapon Case 3','CS20 Case','Danger Zone Case','eSports 2013 Case',
        'eSports 2013 Winter Case','eSports 2014 Summer Case','Falchion Case','Gamma 2 Case','Gamma Case',
        'Glove Case','Horizon Case','Huntsman Weapon Case','Operation Bravo Case','Operation Breakout Weapon Case',
        'Operation Hydra Case','Operation Phoenix Weapon Case','Operation Vanguard Weapon Case','Operation Wildfire Case','Prisma 2 Case',
        'Prisma Case','Revolver Case','Shadow Case','Shattered Web Case','Spectrum 2 Case','Spectrum Case',
        'Winter Offensive Weapon Case']

users = ['uraniumiscute','seven_hack69', 'ClaudiuFilip110']
req = 'https://steamcommunity.com/id/' + users[2] +'/inventory/json/730/2'
r = requests.get(req)
theJSON = r.json()

inventory = theJSON["rgInventory"]
descriptions = theJSON["rgDescriptions"]
#initialize the DICT with the available cases
Cases = {}
for key in descriptions:
    item = descriptions[key]
    if " Case" in item["name"]:
        _case = item["name"]
        Cases[_case] = 0
#get number of cases in dict
for key in descriptions:
    item = descriptions[key]
    if " Case" in item["name"]:
        for invent in inventory:
            x = inventory[invent]
            if  item["classid"] == x["classid"]:
                Cases[item["name"]] += 1

MARKET = []
#-----------pickle module
print('Do you want to refresh the market? (Y / N) ', end='')
market_refresh = str(input())
market_refresh = market_refresh.upper()
if market_refresh != 'Y':
    pickle_in = open("current_market.pickle", "rb")
    MARKET = pickle.load(pickle_in)
else:
    for i in range(len(data)):
        case = str(data[i][0])
        before_replace = case
        case = case.replace(' ','%20').replace(':','%3A')
        req = 'https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=' + case
        #wait 3 seconds because the server doesn't allow more than 20 queries/ min.
        time.sleep(3)
        r = requests.post(req)
        MARKET.append(r.json()['lowest_price'])
        #print('loading...')
        print(before_replace, r.json()['lowest_price'], 'CORRECT' if r.status_code == 200 else 'INCORRECT')
        with open("current_market.pickle","wb") as f:
            pickle.dump(MARKET, f)

#CASES
cases = data
print(cases)
#QTY of cases
QTY = [0 for i in range(len(cases))]
for key in descriptions:
    item = descriptions[key]
    if " Case" in item["name"]:
        if item["name"] in cases:
            #add qty at the right index
            QTY[cases.index(item["name"])] = Cases[item["name"]]

#MARKET
MARKET_CUT = []
float_market = []
float_market_rounded = [0 for i in range(len(QTY))]

for i in MARKET:
    float_market.append(float(i.replace('€','').replace(',','.').replace('--','00')))
for i in range(len(float_market)):
    float_market_rounded[i] = round(float_market[i]/1.149-0.01,2)
    
#TOTAL
TOTAL = [0 for i in range(32)]
for i in range(len(QTY)):
    TOTAL[i] = QTY[i] * float_market[i]

#TOTAL w~ CUT
TOTAL_CUT = [0 for i in range(32)]
for i in range(len(QTY)):
    TOTAL_CUT[i] = QTY[i] * float_market_rounded[i]
df = {
    'CASES': cases,
    'QTY': QTY,
    'MARKET': MARKET,
    'MARKET w~ CUT': float_market_rounded,
    'TOTAL': TOTAL,
    'TOTAL w~ CUT': TOTAL_CUT,
}
table = pd.DataFrame(data=df)
print(table)




















