import csv
import codecs
from PySide2.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from PySide2.QtCore import QDir
#from window import widgetWindow
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
                results = addToResults(results, betrag, jahr, monat, 'Einnahmen', chosenCat)
            elif resultIdent == -1:
                print('Aborted!')
                break
            print(str(counter) + ': ' + chosenCat + '(income)\n' + displayText + '\n')
        elif 0 < len(catFound):
            if 1 < len(catFound) and not all([catFound[0] == elm for elm in catFound]):
                print('Multiple different identifiers found!')
                print(date)
                print(searchText)
                print(', '.join(catFound))
            results = addToResults(results, betrag, jahr, monat, catFound[0], '')
            print(str(counter) + ': ' + catFound[0] + '(auto identified)\n   ' + displayText + '\n')
        else:
            resultIdent, chosenCat, catIdent = findCat(window, displayText, miscList)

            # switch the user input
            if resultIdent == 1:
                identifierDict[catIdent.lower()] = chosenCat
                identifiers.append(catIdent.lower())
                if not identifiersAdded:
                    identifiersAdded = True
                results = addToResults(results, betrag, jahr, monat, chosenCat, '')
            elif resultIdent == 2: # Too singular, no identifiers added
                results = addToResults(results, betrag, jahr, monat, chosenCat, '')
            elif resultIdent == 3: # Sonstiges
                if catIdent not in miscList:
                    miscList.append(catIdent)
                results = addToResults(results, betrag, jahr, monat, chosenCat, catIdent)
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


def addToResults(results, betrag, jahr, monat, cat, catIdent):
    if jahr in results:
        if monat in results[jahr]:
            if cat in results[jahr][monat]:
                if catIdent == '':
                    results[jahr][monat][cat] += betrag
                elif catIdent in results[jahr][monat][cat]:
                    results[jahr][monat][cat][catIdent] += betrag
            elif not catIdent == '':
                results[jahr][monat][cat] = {}
                results[jahr][monat][cat][catIdent] = betrag
            else:
                results[jahr][monat][cat] = betrag
        elif not catIdent == '':
            results[jahr][monat] = {}
            results[jahr][monat][cat] = {}
            results[jahr][monat][cat][catIdent] = betrag
        else:
            results[jahr][monat] = {}
            results[jahr][monat][cat] = betrag

    elif not catIdent == '':
        results[jahr] = {}
        results[jahr][monat] = {}
        results[jahr][monat][cat] = {}
        results[jahr][monat][cat][catIdent] = betrag
    else:
        results[jahr] = {}
        results[jahr][monat] = {}
        results[jahr][monat][cat] = betrag
    return results


def findCat(window, displayText, miscList):
    while True:
        catText = 'Zur folgenden Buchung wurde keine Kategorie gefunden:\n' + \
            displayText + '\nIn welche Kategorie passt die Buchung?'
        categories = getCategories()
        if -1 < displayText.lower().find('amazon'):
            startIdx = categories.index('Sonstiges')
        else:
            startIdx = 0

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
            # Amazon special thingy
            if -1 < displayText.lower().find('amazon'):
                if 'Amazon' in miscList:
                    startIdx = miscList.index('Amazon')
                elif 'amazon' in miscList:
                    startIdx = miscList.index('amazon')
                else:
                    miscList.append('Amazon')
                    startIdx = miscList.index('Amazon')
            else:
                startIdx = 0
            catIdent, ok = QInputDialog().getItem(window, "DKB Auswertung",
                                                  identText, miscList, startIdx, True)
            if ok and catIdent != "":
                return [3, chosenCat, catIdent] # Beschreibenden Text auswerten
            else:
                abort = abortDialog()
                if abort:
                    return [-1, 0, 0]
        elif ok and chosenCat == ignoreText:
            return [0, 0, 0]
        else:
            abort = abortDialog()
            if abort:
                return [-1, 0, 0]

def findIncome(window, displayText):
    while True:
        catText = 'Zu welcher Kategorie gehören folgende Einnahmen:\n' + displayText
        incomeOptions = ['Gehalt Georg', 'Gehalt Franzi', 'BAFöG', 'Erstattung Versicherung',
                         'Unterhalt', ignoreText]

        chosenCat, ok = QInputDialog().getItem(window, "DKB Auswertung",
                                               catText, incomeOptions, 0, True)

        if ok and not chosenCat == '' and not chosenCat == ignoreText:
            return [1, chosenCat]
        if ok and chosenCat == ignoreText:
            return [0, '']
        else:
            abort = abortDialog()
            if abort:
                return [-1, '']


def abortDialog():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText("Soll die Auswertung abgebrochen werden?")
    msg.setInformativeText("Keine Auswertung wird erstellt.\n" +
                           "Wenn dieses Fenster abgebrochen wird, wird der Dialog wiederholt.")
    msg.setWindowTitle("DKB Auswertung")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Cancel)

    retval = msg.exec_()

    if retval == QMessageBox.Ok:
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

def getCategories():
    categoryList = ['Supermarkt', 'Essen gehen', 'Drogerie', 'Apotheke', 'Handy',
                    'Wohnung', 'Kleidung', 'Miete', 'Transport', 'Versicherung',
                    'Post', 'Geld abheben', 'Monatlich', 'Sonstiges', ignoreText]
    return categoryList

