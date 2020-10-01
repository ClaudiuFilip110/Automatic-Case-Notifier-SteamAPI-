import requests
import pandas as pd
import time
import pickle
import os
from pprint import pprint

# ---------------------------------------CONSTANTS
YES_INPUT = 'Y'
WAIT_TIME = 3
STATUS_OK = 200


# ---------------------------------------MAIN BODY
def main():
    # initialize data
    casesList = getCases()
    users = getUsers()
    theJSON = getRequest(users)
    if theJSON is None:
        print("Steam inventory is unavailable")
        return None

    # initialize inventory and description
    inventory = theJSON["rgInventory"]
    descriptions = theJSON["rgDescriptions"]
    userCases = populateDict(descriptions, inventory)
    if not userCases:
        print("Cases is empty")
        return None

    # initialize data from pickle
    pickleDataFrame, PICKLE_MARKET = initPickleDataFrame(
        casesList, userCases, descriptions)
    print("Stored data in pickle: ")
    print(pickleDataFrame)

    # if input is other than y/Y we start getting the current market's prices
    userInput = getUserInput()
    if userInput != YES_INPUT:
        pass
    else:
        STEAM_MARKET = getCurrentPricesFromMarket(casesList)
        if len(STEAM_MARKET) == 0:
            return None
        steamDataFrame = initSteamDataFrame(casesList, STEAM_MARKET)
        if STEAM_MARKET:
            print(steamDataFrame)
        else:
            print("steam prices not available")

        #finish this
        compareDataFrame = initCompareDataFrame(
            casesList, STEAM_MARKET, PICKLE_MARKET, pickleDataFrame, steamDataFrame)
        if not compareDataFrame.empty:
            print(compareDataFrame)
        else:
            print("compare data frame is empty")


# ---------------------------------------FUNCTIONS
def getCases():
    return ['Chroma 2 Case', 'Chroma 3 Case', 'Chroma Case', 'Clutch Case', 'CS:GO Weapon Case',
            'CS:GO Weapon Case 2', 'CS:GO Weapon Case 3', 'CS20 Case', 'Danger Zone Case', 'eSports 2013 Case',
            'eSports 2013 Winter Case', 'eSports 2014 Summer Case', 'Falchion Case', 'Fracture Case', 'Gamma 2 Case', 'Gamma Case',
            'Glove Case', 'Horizon Case', 'Huntsman Weapon Case', 'Operation Bravo Case', 'Operation Breakout Weapon Case',
            'Operation Hydra Case', 'Operation Phoenix Weapon Case', 'Operation Vanguard Weapon Case', 'Operation Wildfire Case', 'Prisma 2 Case',
            'Prisma Case', 'Revolver Case', 'Shadow Case', 'Shattered Web Case', 'Spectrum 2 Case', 'Spectrum Case',
            'Winter Offensive Weapon Case']


def getUsers():
    return ['uraniumiscute', 'seven_hack69', 'ClaudiuFilip110']


def getRequest(users):
    req = 'https://steamcommunity.com/id/' + users[1] + '/inventory/json/730/2'
    try:
        r = requests.get(req)
    except:
        print("Status code:", r.status_code)
        print("bad request OR server unavailable")
        quit()
    finally:
        try:
            theJSON = r.json()
        except e:
            print(f"Error is {e.toString()}")
    return theJSON


def initDict(descriptions):
    # initialize the DICT with the available cases
    Cases = {}
    for key in descriptions:
        item = descriptions[key]
        if " Case" in item["name"]:
            _case = item["name"]
            Cases[_case] = 0
    return Cases


def populateDict(descriptions, inventory):
    Cases = initDict(descriptions)
    # get number of cases in dict
    for key in descriptions:
        item = descriptions[key]
        if " Case" in item["name"]:
            for invent in inventory:
                x = inventory[invent]
                if item["classid"] == x["classid"]:
                    Cases[item["name"]] += 1
    return Cases


def getCurrentPricesFromMarket(data):
    STEAM_MARKET = []
    for i in range(len(data)):
        caseName = data[i]
        req = f'https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name={convertToJsonData(data[i])}'

        # wait 3 seconds because the server doesn't allow more than 20 queries/ min.
        time.sleep(WAIT_TIME)
        r = requests.post(req)
        if(r.status_code == STATUS_OK):
            STEAM_MARKET.append(r.json()['lowest_price'])
            print(caseName, r.json()['lowest_price'],
                  'Response from server:', str(r.status_code))
        # ------ this saves in pickle
        # with open("current_market.pickle", "wb") as f:
        #     pickle.dump(STEAM_MARKET, f)
    return STEAM_MARKET


def getUserInput():
    print('Do you want to compare the market prices with your stored prices? (Y / N) ', end='')
    return str(input()).upper()


def convertToJsonData(case):
    return case.replace(' ', '%20').replace(':', '%3A')


def initCasesQTY(cases, Cases, descriptions):
    # QTY of cases
    QTY = [0 for i in range(len(cases))]
    for key in descriptions:
        item = descriptions[key]
        if " Case" in item["name"]:
            if item["name"] in cases:
                # add qty at the right index
                QTY[cases.index(item["name"])] = Cases[item["name"]]
    return QTY


def loadDataFromPickle():
    fromPickle = open("current_market.pickle", "rb")
    PICKLE_MARKET = []
    PICKLE_MARKET = pickle.load(fromPickle)
    return PICKLE_MARKET


def initMarketPrices(cases, PICKLE_MARKET):
    float_market = []
    float_market_rounded = [0 for i in range(len(cases))]
    # convert from string to float
    for i in PICKLE_MARKET:
        float_market.append(
            float(i.replace('€', '').replace(',', '.').replace('--', '00')))
    # convert from uncut to cut price
    for i in range(len(float_market)):
        float_market_rounded[i] = round(float_market[i]/1.149-0.01, 2)
    return float_market, float_market_rounded


def initTotal(cases, QTY, float_market):
    TOTAL = [0 for i in range(len(cases))]
    for i in range(len(cases)):
        TOTAL[i] = QTY[i] * float_market[i]
    return TOTAL


def initTotalWithCut(cases, QTY, float_market_rounded):
    TOTAL_CUT = [0 for i in range(len(cases))]
    for i in range(len(TOTAL_CUT)):
        TOTAL_CUT[i] = QTY[i] * float_market_rounded[i]
    return TOTAL_CUT


def initPickleDataFrame(casesList, userCases, descriptions):
    casesQTY = initCasesQTY(casesList, userCases, descriptions)
    PICKLE_MARKET = loadDataFromPickle()
    # MARKET
    float_market, float_market_cut = initMarketPrices(casesList, PICKLE_MARKET)
    # TOTAL
    TOTAL = initTotal(casesList, casesQTY, float_market)
    # TOTAL w~ CUT
    TOTAL_CUT = initTotalWithCut(casesList, casesQTY, float_market_cut)
    pickle_data = {
        'CASES': casesList,
        'QTY': casesQTY,
        'MARKET': float_market,
        'MARKET w~ CUT': float_market_cut,
        'TOTAL': TOTAL,
        'TOTAL w~ CUT': TOTAL_CUT,
    }
    return pd.DataFrame(data=pickle_data), PICKLE_MARKET


def initSteamDataFrame(casesList, STEAM_MARKET):
    float_steam = []
    for price in STEAM_MARKET:
        float_steam.append(
            float(price.replace('€', '').replace(',', '.').replace('--', '00')))
    steam_data = {
        'CASES': casesList,
        'STEAM': float_steam
    }
    return pd.DataFrame(data=steam_data)


def initCompareDataFrame(casesList, STEAM_MARKET, PICKLE_MARKET, pickle, steam):
    steam_market_series = [0 for i in range(len(casesList))]
    for i in range(len(STEAM_MARKET)):
        steam_market_series[i] = str(STEAM_MARKET[i]) + '€'

    compare_data = {
        'CASES': casesList,
        'PICKLE': PICKLE_MARKET,
        'MARKET': STEAM_MARKET,
        'DIFF': pickle['MARKET'] - steam['STEAM']
    }
    return pd.DataFrame(data=compare_data)


if __name__ == "__main__":
    main()
