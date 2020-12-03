import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
from functions.dkbReader import sort_csvdata, mergeFiles
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
        gridLayout.addWidget(self.addEntriesButton, 6, 1, 1, 3)

        self.setLayout(gridLayout)

        ## SIGNALS / SLOTS ##
        self.csvSearchButton.clicked.connect(self.find_csv_file)
        self.resultsButton.clicked.connect(self.call_dkb_reader)
        self.loadResultsButton.clicked.connect(self.loadResults)
        self.pathChanged.connect(self.pathText.setText)

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


