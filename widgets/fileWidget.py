import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
from functions.dkbReader import sort_csvdata, mergeFiles, addToResults
from widgets.manualEntryDialog import ManualEntryDialog
from widgets.meterDialog import MeterDialog
import datetime
import pickle
import shutil

#TODO: Create merge function

class FileWidget(QtWidgets.QWidget):
    pathChanged = Signal(str)
    updateTree = Signal(dict)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.results = None

        ## FILE SEARCH WIDGETS ##
        self.csvSearchButton = QtWidgets.QPushButton(".csv-Datei auswählen")
        self.csvSearchButton.setMaximumWidth(250)
        self.resultsButton = QtWidgets.QPushButton("Datei auswerten")
        self.resultsButton.setMaximumWidth(250)
        self.loadResultsButton = QtWidgets.QPushButton("Auswertung laden")
        self.loadResultsButton.setMaximumWidth(250)
        self.addEntriesButton = QtWidgets.QPushButton("Daten Manuell hinzufügen")
        self.addEntriesButton.setMaximumWidth(250)
        self.addEntriesButton.setVisible(False)
        self.meterButton = QtWidgets.QPushButton("Zählerstand hinzufügen")
        self.meterButton.setMaximumWidth(250)
        self.meterButton.setVisible(False)
        self.pathText = QtWidgets.QTextEdit("")
        self.pathText.setReadOnly(True)
        self.pathText.setFixedHeight(self.pathText.size().height() / 8)
        self.pathText.setMaximumWidth(250)
        self.pathLabel = QtWidgets.QLabel("Pfad")
        self.pathLabel.setFixedWidth(50)
        self.orLabel = QtWidgets.QLabel("ODER")
        self.orLabel.setFixedWidth(250)
        self.orLabel.setAlignment(QtCore.Qt.AlignCenter)

        ## LAYOUT ##
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(self.csvSearchButton, 0, 1, 1, 3)
        gridLayout.addWidget(self.pathLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.pathText, 1, 1, 1, 3)
        gridLayout.addWidget(self.resultsButton, 2, 1, 1, 3)
        gridLayout.addWidget(self.orLabel, 3, 0, 1, 4)
        gridLayout.addWidget(self.loadResultsButton, 4, 1, 1, 3)
        gridLayout.addWidget(self.addEntriesButton, 5, 1, 1, 3)
        gridLayout.addWidget(self.meterButton, 6, 1, 1, 3)

        self.setLayout(gridLayout)

        ## SIGNALS / SLOTS ##
        self.csvSearchButton.clicked.connect(self.find_csv_file)
        self.resultsButton.clicked.connect(self.call_dkb_reader)
        self.loadResultsButton.clicked.connect(self.loadResults)
        self.pathChanged.connect(self.pathText.setText)
        self.addEntriesButton.clicked.connect(self.manuallyAdd)
        self.meterButton.clicked.connect(self.addMeter)


    @Slot()
    def find_csv_file(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Load .csv file',
                                            QtCore.QDir().home().path() + '/Downloads', "CSV (*.csv)")
        self.pathChanged.emit(fname[0])
        # self.results = pickle.load(open("dkbTestResults.p", "rb"))
        # self.updateTree.emit(self.results)

    @Slot()
    def call_dkb_reader(self):
        self.results = sort_csvdata(self)
        self.saveResults(self.results)
        self.addEntriesButton.setVisible(True)
        self.meterButton.setVisible(True)
        self.updateTree.emit(self.results)

    @Slot()
    def test(self, item, column):
        Test = 1


    @Slot()
    def loadResults(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        current_parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
        results_path = os.path.join(current_parent_path, "data")
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load results',
                                                            results_path, "Pickle files (*.p)")
        try:
            results = pickle.load(open(fileName, "rb"))
            self.results = results
            print("Succesfully loaded: " + fileName)
            self.addEntriesButton.setVisible(True)
            self.meterButton.setVisible(True)
            self.updateTree.emit(self.results)
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)

            msg.setText("Datei konnte nicht geladen werden")
            msg.setInformativeText("Bitte erneut versuchen oder neue Datei auslesen.")
            msg.setWindowTitle("DKB Auswertung")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)

            msg.exec_()


    def saveResults(self, results):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)

        msg.setText("Soll die Auswertung gespeichert werden?")
        msg.setWindowTitle("DKB Auswertung")
        yesButton = msg.addButton('Ja',QtWidgets.QMessageBox.YesRole)
        msg.addButton('Nein', QtWidgets.QMessageBox.NoRole)
        msg.setDefaultButton(yesButton)

        retval = msg.exec_()

        if retval == 0:
            if os.path.isfile("data/lastResults.p"):
                currentDate = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
                os.rename(r"data/lastResults.p", r"data/oldResults_" + currentDate + ".p")
            pickle.dump(results, open("data/lastResults.p", "wb"))


    @Slot()
    def mergeResults(self, selection):
        # assemble selected results
        selectRes = self.results
        for year in list(selection.keys()):
            b_any = False
            for month in list(selection[year].keys()):
                if not selection[year][month]:
                    selectRes[int(year)].pop(month, None)
                elif not b_any:
                    b_any = True
            if not b_any:
                selectRes.pop(int(year), None)

        if not selectRes:  # all elements were purged
            return

        fileFound = False
        try:
            allData = pickle.load(open('data/_AllResults.p', 'rb'))
            fileFound = True
        except:
            pass

        if fileFound:
            newAllData = mergeFiles(allData, selectRes)
            currentDate = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            shutil.copy2("data/_AllResults.p", "data/archive/_oldAllResults_" + currentDate + ".p")
            print('Results successfully merged')
        else:
            newAllData = selectRes
            print('New overall file created')

        pickle.dump(newAllData, open('data/_AllResults.p', 'wb'))
        print('Results successfully saved')


    @Slot()
    def manuallyAdd(self):
        resultsUpdated = False
        while(True):
            # do dialog
            dialogData = ManualEntryDialog.doManualEntry()
            if not dialogData['result']:
                break
            monthlist = ['',
                         'Januar', 'Februar', 'März', 'April',
                         'Mai', 'Juni', 'Juli', 'August',
                         'September', 'Oktober', 'November', 'Dezember']

            # sort data
            month = monthlist[dialogData['date'][1]]
            incSpe = dialogData['incSpe']
            if incSpe == 'Ausgaben' or incSpe == 'Einnahmen':
                bch = {
                    'Buchung_Tag': dialogData['date'][2],
                    'Buchung_Monat': dialogData['date'][1],
                    'Buchung_Jahr': dialogData['date'][0],
                    'Verwendungszweck': dialogData['descr'],
                    'Buchungstext': 'Manuell'
                }
                if incSpe == 'Ausgaben':
                    bch['Betrag'] = str(-dialogData['amt'])
                    self.results = addToResults(self.results, bch, dialogData['amt'], dialogData['date'][0], month, dialogData['cat'], dialogData['catIdent'])
                elif incSpe == 'Einnahmen':
                    bch['Betrag'] = str(-dialogData['amt'])
                    self.results = addToResults(self.results, bch, dialogData['amt'], dialogData['date'][0], month, 'Einnahmen', dialogData['cat'])

            resultsUpdated = True

            # ask for repetition
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)

            msg.setText("Sollen weitere Einträge hinzugefügt werden?")
            msg.setWindowTitle("DKB Auswertung")
            yesButton = msg.addButton('Ja', QtWidgets.QMessageBox.YesRole)
            msg.addButton('Nein', QtWidgets.QMessageBox.NoRole)
            msg.setDefaultButton(yesButton)

            retval = msg.exec_()

            if retval != 0:
                break
        if resultsUpdated:
            self.saveResults(self.results)
            self.updateTree.emit(self.results)

    @Slot()
    def addMeter(self):
        resultsUpdated = False
        while (True):
            # do dialog
            dialogData = MeterDialog.doMeter()
            if not dialogData['result']:
                break
            monthlist = ['',
                         'Januar', 'Februar', 'März', 'April',
                         'Mai', 'Juni', 'Juli', 'August',
                         'September', 'Oktober', 'November', 'Dezember']

            # sort data
            month = monthlist[dialogData['date'][1]]
            meterType = dialogData['meterType']
            bch = {
                'Ablesung_Tag': dialogData['date'][2],
                'Ablesung_Monat': dialogData['date'][1],
                'Ablesung_Jahr': dialogData['date'][0],
                'Zählerstand': dialogData['level']
            }
            self.results = addToResults(self.results, bch, dialogData['level'], dialogData['date'][0], month,
                                        'Zählerstände', dialogData['meterType'])

            resultsUpdated = True

            # ask for repetition
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)

            msg.setText("Sollen weitere Einträge hinzugefügt werden?")
            msg.setWindowTitle("DKB Auswertung")
            yesButton = msg.addButton('Ja', QtWidgets.QMessageBox.YesRole)
            msg.addButton('Nein', QtWidgets.QMessageBox.NoRole)
            msg.setDefaultButton(yesButton)

            retval = msg.exec_()

            if retval != 0:
                break
        if resultsUpdated:
            self.saveResults(self.results)
            self.updateTree.emit(self.results)


