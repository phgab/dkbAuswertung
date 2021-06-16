import csv
import codecs
from PySide2.QtWidgets import QInputDialog, QLineEdit, QMessageBox
import pickle

ignoreText = 'Diesen Eintrag ignorieren'




def dkbReadCSV(fileName):
    with codecs.open(fileName,'r','iso-8859-1') as csv_file:
        csv_reader = list(csv.reader(csv_file, delimiter=';'))
        line_count_start = 7
        numRows = len(csv_reader)
        line_count = 0
        csvData = []
        for row in reversed(csv_reader):
            #if line_count == line_count_start:
            #    print(f'Column names are {", ".join(row)}')
            if line_count < numRows - line_count_start:
                # print('Content in line ' + str(line_count) + f': {", ".join(row)}')
                buchung = row[0].split('.')
                wertstellung = row[1].split('.')
                rowData = {
                    "Buchung_Tag": int(buchung[0]),
                    "Buchung_Monat": int(buchung[1]),
                    "Buchung_Jahr": int(buchung[2]),
                    "Wertstellung_Tag": int(wertstellung[0]),
                    "Wertstellung_Monat": int(wertstellung[1]),
                    "Wertstellung_Jahr": int(wertstellung[2]),
                    "Buchungstext": row[2],
                    "Auftraggeber": row[3],
                    "Verwendungszweck": row[4],
                    "Kontonummer": row[5],
                    "BLZ": row[6],
                    "Betrag": row[7],
                    "Glaeubiger-ID": row[8],
                    "Mandatsreferenz": row[9],
                    "Kundenreferenz": row[10]
                }

                csvData.append(rowData)
            line_count += 1
        print(f'Processed {line_count} lines.')
    return csvData


def sort_csvdata(window):

    fileName = window.pathText.toPlainText()
    csvData = dkbReadCSV(fileName)
    results = iterate_csvdata(window, csvData)
    return results


def iterate_csvdata(window,csvData):
    results = {}

    identifierDict = pickle.load(open("data/identifierDict.p", "rb"))
    identifiers = list(identifierDict.keys())
    identifiersAdded = False
    miscList =[''] # Liste mit 'Sonstiges'-Einträgen

    for counter, bch in enumerate(csvData):
        auftraggeber = bch["Auftraggeber"]
        verwendungszweck = bch["Verwendungszweck"]
        jahr, monat, date = getDateFromBch(bch)
        betrag = float(bch["Betrag"].replace('.', '').replace(',', '.'))

        searchText = auftraggeber.lower() + ', ' + verwendungszweck.lower()

        catFound = [identifierDict[key] for key in identifiers if -1 < searchText.find(key)]
        displayText = date + ':\n' + auftraggeber + ';\n' + verwendungszweck + '\n' + str(betrag) + ' €'

        if 0 < betrag:
            resultIdent, chosenCat = findIncome(window, displayText)
            if resultIdent == 1:
                results = addToResults(results, bch, betrag, jahr, monat, 'Einnahmen', chosenCat)
                print(str(counter) + ': ' + chosenCat + '(income)\n' + displayText + '\n')
            elif resultIdent == 0:
                print(str(counter) + ': Ignored')
            elif resultIdent == -1:
                print('Aborted!')
                break

        elif 0 < len(catFound):
            if 1 < len(catFound) and not all([catFound[0] == elm for elm in catFound]):
                print('Multiple different identifiers found!')
                print(date)
                print(searchText)
                print(', '.join(catFound))
            results = addToResults(results, bch, -betrag, jahr, monat, catFound[0], '')
            print(str(counter) + ': ' + catFound[0] + '(auto identified)\n   ' + displayText + '\n')
        else:
            resultIdent, chosenCat, catIdent = findCat(window, displayText, miscList)

            # switch the user input
            if resultIdent == 1:
                identifierDict[catIdent.lower()] = chosenCat
                identifiers.append(catIdent.lower())
                if not identifiersAdded:
                    identifiersAdded = True
                results = addToResults(results, bch, -betrag, jahr, monat, chosenCat, '')
            elif resultIdent == 2: # Too singular, no identifiers added
                results = addToResults(results, bch, -betrag, jahr, monat, chosenCat, '')
            elif resultIdent == 3: # Sonstiges
                if catIdent not in miscList:
                    miscList.append(catIdent)
                results = addToResults(results, bch, -betrag, jahr, monat, chosenCat, catIdent)
            elif resultIdent == -1:
                print('Aborted!')
                break
            else:
                print(str(counter) + ': Nothing')
                continue
            print(str(counter) + ': ' + chosenCat + ' (identification: ' + str(catIdent) + ')\n   ' + displayText + '\n')

    if identifiersAdded:
        pickle.dump(identifierDict, open("data/identifierDict.p", "wb"))
    return results


def addToResults(results, bch, betrag, jahr, monat, cat, catIdent):
    if jahr in results:
        if monat in results[jahr]:
            if cat in results[jahr][monat]:
                if not catIdent == '':
                    if catIdent not in results[jahr][monat][cat]:
                        results[jahr][monat][cat][catIdent] = {'sum': 0, 'bch': []}
            elif not catIdent == '':
                results[jahr][monat][cat] = {}
                results[jahr][monat][cat][catIdent] = {'sum': 0, 'bch': []}
            else:
                results[jahr][monat][cat] = {'sum': 0, 'bch': []}
        elif not catIdent == '':
            results[jahr][monat] = {}
            results[jahr][monat][cat] = {}
            results[jahr][monat][cat][catIdent] = {'sum': 0, 'bch': []}
        else:
            results[jahr][monat] = {}
            results[jahr][monat][cat] = {'sum': 0, 'bch': []}

    elif not catIdent == '':
        results[jahr] = {}
        results[jahr][monat] = {}
        results[jahr][monat][cat] = {}
        results[jahr][monat][cat][catIdent] = {'sum': 0, 'bch': []}
    else:
        results[jahr] = {}
        results[jahr][monat] = {}
        results[jahr][monat][cat] = {'sum': 0, 'bch': []}

    if catIdent == '':
        results[jahr][monat][cat]['sum'] += betrag
        results[jahr][monat][cat]['bch'].append(bch)
    else:
        results[jahr][monat][cat][catIdent]['sum'] += betrag
        results[jahr][monat][cat][catIdent]['bch'].append(bch)
    return results


def findCat(window, displayText, miscList):
    while True:
        catText = 'Zur folgenden Buchung wurde keine Kategorie gefunden:\n' + \
            displayText + '\nIn welche Kategorie passt die Buchung?'
        categories = getCatSpe()
        suggestList = pickle.load(open("data/suggestList.p", "rb"))
        suggestFound = False
        startIdx = 0
        for itm in list(suggestList.keys()):
            if -1 < displayText.lower().find(itm.lower()):
                try:
                    startIdx = categories.index(suggestList[itm][0])
                    suggestFound = True
                except:
                    continue

                try:
                    suggestCatIdent = suggestList[itm][1]
                except:
                    pass
                break

        chosenCat, ok = QInputDialog().getItem(window, "DKB Auswertung",
                                               catText, categories, startIdx, False)

        if ok and chosenCat != ignoreText and chosenCat != "Sonstiges":
            identTextStart = ''
            while True:
                identText = identTextStart + 'Welches Wort im Buchungstext kann die Kategorie ' + chosenCat + \
                          ' eindeutig identifizieren?\n' + displayText

                catIdent, ok = QInputDialog().getText(window, "DKB Auswertung",
                                                      identText, QLineEdit.Normal, "")
                if ok and catIdent != "":
                    if -1 < displayText.lower().find(catIdent.lower()):
                        break
                    else:
                        identTextStart = 'Die eingegebene Zeichenfolge konnte im Buchungstext nicht gefunden werden! Bitte erneut eingeben\n'
                else:
                    break
            if ok and catIdent != "":
                return [1, chosenCat, catIdent] # identifierDict ergänzen
            else:
                return [2, chosenCat, 0] # Nicht ergänzen
        elif ok and chosenCat == "Sonstiges":
            identText = 'Was soll als Beschreibung zu Sonstiges angezeigt werden?\n' + displayText
            # Handle suggestions
            if suggestFound:
                if suggestCatIdent not in miscList:
                    miscList.append(suggestCatIdent)
                startIdx = miscList.index(suggestCatIdent)
            else:
                startIdx = 0
            while True:
                catIdent, ok = QInputDialog().getItem(window, "DKB Auswertung",
                                                      identText, miscList, startIdx, True)
                if ok and catIdent != "":
                    return [3, chosenCat, catIdent] # Beschreibenden Text auswerten
                elif ok and catIdent == "":
                    doNone = emptyMiscDescrDialog()
                    if doNone:
                        return [3, chosenCat, 'None']  # Beschreibenden Text auswerten
                else:
                    abort = abortDialog()
                    if abort:
                        return [-1, 0, 0]
                    break

        elif ok and chosenCat == ignoreText:
            return [0, 0, 0]
        else:
            abort = abortDialog()
            if abort:
                return [-1, 0, 0]

def findIncome(window, displayText):
    while True:
        catText = 'Zu welcher Kategorie gehören folgende Einnahmen:\n' + displayText
        incomeOptions = getCatInc()

        suggestList = pickle.load(open("data/suggestList.p", "rb"))
        startIdx = 0
        for itm in list(suggestList.keys()):
            if -1 < displayText.lower().find(itm.lower()):
                try:
                    startIdx = incomeOptions.index(suggestList[itm][0])
                    break
                except:
                    pass

        chosenCat, ok = QInputDialog().getItem(window, "DKB Auswertung",
                                               catText, incomeOptions, startIdx, True)

        if ok and not chosenCat == '' and not chosenCat == ignoreText:
            return [1, chosenCat]
        if ok and chosenCat == ignoreText:
            return [0, '']
        else:
            abort = abortDialog()
            if abort:
                return [-1, '']


def abortDialog():
    msgText = "Soll die Auswertung abgebrochen werden?"
    msgInfoText = "Keine Auswertung wird erstellt.\n" + \
                  "Wenn dieses Fenster abgebrochen wird, wird der Dialog wiederholt."
    msgTitle = "DKB Auswertung"
    retval = yesNoDialog(msgText, msgInfoText, msgTitle)

    return retval


def emptyMiscDescrDialog():
    msgText = "Soll keine Beschreibung eingetragen werden?"
    msgInfoText = "As Beschreibung wird 'None' eingetragen.\n" + \
                  "Wenn dieses Fenster abgebrochen wird, wird der Dialog wiederholt."
    msgTitle = "DKB Auswertung"
    retval = yesNoDialog(msgText, msgInfoText, msgTitle)

    return retval


def yesNoDialog(msgText, msgInfoText, msgTitle):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText(msgText)
    msg.setInformativeText(msgInfoText)
    msg.setWindowTitle(msgTitle)
    yesButton = msg.addButton('Ja', QMessageBox.YesRole)
    msg.addButton('Nein', QMessageBox.NoRole)
    msg.setDefaultButton(yesButton)

    retval = msg.exec_()

    if retval == 0:
        return True
    else:
        return False

def getDateFromBch(bch):
    monthlist = ['',
                 'Januar', 'Februar', 'März', 'April',
                 'Mai', 'Juni', 'Juli', 'August',
                 'September', 'Oktober', 'November', 'Dezember']
    tag = bch["Buchung_Tag"]
    monat = monthlist[bch["Buchung_Monat"]]
    jahr = bch["Buchung_Jahr"]
    datestr = str(tag) + ". " + monat + " " + str(jahr)
    return [jahr, monat, datestr]


def getCatSpe():
    categoryList = ['Supermarkt', 'Essen gehen', 'Drogerie', 'Apotheke', 'Arzt', 'Handy',
                    'Wohnung', 'Kleidung', 'Miete', 'Transport', 'Versicherung', 'Kind', 'Urlaub/Ausflug',
                    'Post', 'Geld abheben', 'Monatlich', 'Sonstiges', ignoreText]
    return categoryList


def getCatInc():
    categoryList = ['Gehalt Georg', 'Gehalt Franzi', 'BAFöG', 'Erstattung Versicherung',
                    'Unterhalt', 'Sonstiges', ignoreText]
    return categoryList


def mergeFiles(mainRes, newRes): #TODO: REPAIR THIS SHIT
    # brute force: each element in newRes (if months overlap) is compared to all elements of the same month in mainRes
    for year in list(newRes.keys()):
        if year not in mainRes:
            mainRes[year] = newRes[year]
            continue
        for month in list(newRes[year].keys()):
            if month not in mainRes[year]:
                mainRes[year][month] = newRes[year][month]
            # months overlap - start comparing
            for cat in list(newRes[year][month].keys()):
                if 'sum' in newRes[year][month][cat]:  # no subcategories
                    if cat not in mainRes[year][month]:
                        mainRes[year][month][cat] = {'sum': 0, 'bch': []}
                    currentBch = newRes[year][month][cat]['bch']
                    if not currentBch == mainRes[year][month][cat]['bch']:
                        retVal = searchBch(currentBch, mainRes[year][month], cat, None)
                        if retVal is not None:
                            mainRes[year][month] = retVal
                else:  # subcategories
                    if cat not in mainRes[year][month]:
                        mainRes[year][month][cat] = {}
                    for catIdent in list(newRes[year][month][cat].keys()):
                        if catIdent not in mainRes[year][month][cat]:
                            mainRes[year][month][cat][catIdent] = {'sum': 0, 'bch': []}
                        currentBch = newRes[year][month][cat][catIdent]['bch']
                        if not currentBch == mainRes[year][month][cat][catIdent]['bch']:
                            retVal = searchBch(currentBch, mainRes[year][month], cat, catIdent)
                            if retVal is not None:
                                mainRes[year][month] = retVal
    return mainRes


def searchBch(currentBch, compMonth, cat, catIdent): #TODO: REPAIR THIS SHIT
    anyDiff = False
    for bch in currentBch:
        indicesFound = []
        for chkCat in list(compMonth.keys()):
            if 'sum' in compMonth[chkCat]:
                for idx, chkBch in enumerate(compMonth[chkCat]['bch']):
                    if bch == chkBch:
                        indicesFound.append([chkCat, None, idx])
            else:
                for chkCatIdent in list(compMonth[chkCat].keys()):
                    for idx, chkBch in enumerate(compMonth[chkCat][chkCatIdent]['bch']):
                        if bch == chkBch:
                            indicesFound.append([chkCat, chkCatIdent, idx])
        if len(indicesFound) == 1 and indicesFound[0][0] == cat and indicesFound[0][1] == catIdent:
            continue
        elif not anyDiff:
            anyDiff = True

        betrag = float(bch["Betrag"].replace('.', '').replace(',', '.'))
        if betrag < 0:
            betrag *= -1

        for itm in indicesFound:  # pop potential old entries
            if itm[1] is None:
                compMonth[itm[0]]['bch'].pop(itm[2])
                compMonth[itm[0]]['sum'] -= betrag
            else:
                compMonth[itm[0]][itm[1]]['bch'].pop(itm[2])
                compMonth[itm[0]][itm[1]]['sum'] -= betrag

        if catIdent is None:
            compMonth[cat]['bch'].append(bch)
            compMonth[cat]['sum'] += betrag
        else:
            if catIdent in compMonth[cat]:
                compMonth[cat][catIdent]['bch'].append(bch)
                compMonth[cat][catIdent]['sum'] += betrag
            else:
                compMonth[cat][catIdent] = {'sum': betrag, 'bch': bch}

    if anyDiff:
        return compMonth
    else:
        return None
