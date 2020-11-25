
import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
from dkbReader import sort_csvdata
import datetime
import pickle

class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.fileWidget = FileWidget()
        self.selectionWidget = SelectionWidget()

        ## LAYOUT ##
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(self.fileWidget, 0, 0)
        gridLayout.addWidget(self.selectionWidget, 1, 0)
        self.setLayout(gridLayout)


        ## SIGNALS / SLOTS ##
        self.fileWidget.updateTree.connect(self.selectionWidget.updateTree)

    def closeEvent(self, event):
        print('Application closed.')
        if os.path.isfile("data/lastResults.p"):
            currentDate = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            os.rename(r"data/lastResults.p", r"data/oldResults_" + currentDate + ".p")
            print('Files renamed.')


class FileWidget(QtWidgets.QWidget):
    pathChanged = Signal(str)
    updateTree = Signal(dict)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.results = None

        ## FILE SEARCH WIDGETS ##
        csvSearchButton = QtWidgets.QPushButton(".csv-Datei auswählen")
        resultsButton = QtWidgets.QPushButton("Datei auswerten")
        loadResultsButton = QtWidgets.QPushButton("Auswertung laden")
        pathText = QtWidgets.QTextEdit("")
        pathText.setReadOnly(True)
        pathText.setFixedHeight(pathText.size().height() / 8)
        pathLabel = QtWidgets.QLabel("Pfad")
        orLabel = QtWidgets.QLabel("ODER")

        ## LAYOUT ##
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(csvSearchButton, 0, 1, 1, 3)
        gridLayout.addWidget(pathLabel, 1, 0, 1, 1)
        gridLayout.addWidget(pathText, 1, 1, 1, 3)
        gridLayout.addWidget(resultsButton, 2, 1, 1, 3)
        gridLayout.addWidget(orLabel, 3, 2, 1, 2)
        gridLayout.addWidget(loadResultsButton, 4, 1, 1, 3)

        self.setLayout(gridLayout)

        ## SIGNALS / SLOTS ##
        csvSearchButton.clicked.connect(self.find_csv_file)
        loadResultsButton.clicked.connect(self.loadResults)
        self.pathChanged.connect(pathText.setText)

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
        results_path = os.path.join(current_path, "data")
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
        if os.path.isfile("data/lastResults.p"):
            currentDate = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            os.rename(r"data/lastResults.p", r"data/oldResults_" + currentDate + ".p")
        pickle.dump(results, open("data/lastResults.p"))


class SelectionWidget(QtWidgets.QWidget):
    checkboxChanged = Signal(dict)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.selection = None

        ## TREE VIEW WIDGETS ##
        mainTree = QtWidgets.QTreeWidget()
        mainTree.setHeaderLabels(["Jahr", "Monat"])
        mainTree.itemChanged.connect(self.childCheckChanged)
        mainTree.setVisible(False)
        mainTree.setMinimumHeight(200)
        # mainTree.setMaximumHeight(1000)
        self.mainTree = mainTree

        ## LAYOUT ##
        # Do I Really need to do this?!
        treeLayout = QtWidgets.QHBoxLayout()
        treeLayout.addWidget(mainTree)
        self.setLayout(treeLayout)


    @Slot()
    def test(self, item, column):
        Test = 1


    @Slot()
    def updateTree(self, results):
        # To ease writing further on
        checkDict = {False: QtCore.Qt.CheckState.Unchecked, True: QtCore.Qt.CheckState.Checked}

        # Read keys
        newSelect = {}
        years = sorted(list(results.keys()))
        for year in years:
            newSelect[str(year)] = {}
            months = sorted(list(results[year].keys()), key=self.sortMonths)
            for month in months:
                newSelect[str(year)][month] = False

        # Transfer to selection variable
        if self.selection is not None:
            for year in list(self.selection.keys()):
                if year not in newSelect:
                    continue
                for month in list(self.selection[year].keys()):
                    if month in newSelect[year] and newSelect[year][month] == self.selection[year][month]:
                        continue
                    else:
                        newSelect[year][month] = self.selection[year][month]
        self.selection = newSelect

        self.mainTree.clear()
        years = list(self.selection.keys())
        for year in years:
            yearCheckbox = QtWidgets.QTreeWidgetItem()
            yearCheckbox.setText(0, year)
            self.mainTree.addTopLevelItem(yearCheckbox)
            months = list(self.selection[year].keys())
            for month in months:
                monthCheckbox = QtWidgets.QTreeWidgetItem()
                monthCheckbox.setText(1, month)
                monthCheckbox.setCheckState(0, checkDict[self.selection[year][month]])
                yearCheckbox.addChild(monthCheckbox)
        if not self.mainTree.isVisible():
            self.mainTree.setVisible(True)


    @Slot()
    def childCheckChanged(self, item, column):
        if column == 0:
            parent = item.parent()
            year = parent.text(0)
            month = item.text(1)
            if item.checkState(0) == QtCore.Qt.CheckState.Checked:
                value = True
            else:
                value = False
            self.selection[year][month] = value
            # print(str([year, month, value]))
            self.checkboxChanged.emit(self.selection)
            # return [year, month, value]


    def sortMonths(self, str):
        order = ["Januar", "Februar", "März", "April",
                 "Mai", "Juni", "Juli", "August",
                 "September", "Oktober", "November", "Dezember"]
        for num, month in enumerate(order):
            if str == month:
                return num


class PlotWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
