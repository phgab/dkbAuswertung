import matplotlib.pyplot as plt
import numpy as np
import pickle

def test():
    csvRes = pickle.load(open("dkbTestResults.p", "rb"))
    plotExpenses(csvRes)

def plotExpenses(csvRes):
    itemDict, monthList = sortExpenses(csvRes)

    numElem = len(monthList)
    itemNames = list(itemDict.keys())
    ind = np.arange(numElem)
    barWidth = 0.5

    barPlot = []
    for itemName in itemNames:
        print(itemName)
        print(itemDict[itemName])
        barPlot.append(plt.bar(ind, itemDict[itemName], barWidth))

    plt.ylabel('Ausgaben [€]')
    plt.title('Monatliche Ausgaben')
    plt.xticks(ind, monthList)
    plt.legend([p[0] for p in barPlot], itemNames)

    plt.show()

def sortExpenses(csvRes):
    itemDict = {}
    monthList = []
    years = list(csvRes.keys())
    listLength = 0
    for year in years:
        months = list(csvRes[year].keys())
        for month in months:
            results = csvRes[year][month]
            categories = list(results.keys())
            for cat in categories:
                if cat not in itemDict and not cat == 'Einnahmen':
                    itemDict[cat] = [0]*listLength
                if cat == 'Sonstiges':
                    miscSum = 0
                    subcats = list(results[cat].keys())
                    for subcat in subcats:
                        miscSum -= results[cat][subcat]
                    itemDict[cat].append(miscSum)
                elif cat == 'Einnahmen':
                    # SORT SOMEWHERE ELSE
                    test = 1
                else:
                    itemDict[cat].append(-results[cat])
            monthList.append(month + ' ' + str(year))
            listLength += 1
            for cat in list(itemDict.keys()):
                if len(itemDict[cat]) < listLength:
                    itemDict[cat].append(0)
    return [itemDict, monthList]
