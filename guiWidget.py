
import sys
import os
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Signal, Slot
from dkbReader import sort_csvdata
import datetime
import pickle

class mainWidget(QtWidgets.QWidget):
    pathChanged = Signal(str)
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

        ## TREE VIEW WIDGETS ##
        mainTree = QtWidgets.QTreeWidget()
        mainTree.setHeaderLabels(["Jahr", "Monat"])
        mainTree.itemChanged.connect(self.childCheckChanged)
        mainTree.setVisible(False)
        mainTree.setMinimumHeight(200)
        # mainTree.setMaximumHeight(1000)
        self.mainTree = mainTree

        ## LAYOUT ##
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(csvSearchButton, 0, 1, 1, 3)
        gridLayout.addWidget(pathLabel, 1, 0, 1, 1)
        gridLayout.addWidget(pathText, 1, 1, 1, 3)
        gridLayout.addWidget(resultsButton, 2, 1, 1, 3)
        gridLayout.addWidget(orLabel, 3, 2, 1, 2)
        gridLayout.addWidget(loadResultsButton, 4, 1, 1, 3)
        gridLayout.addWidget(mainTree, 5, 0, 1, 4)

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
        # self.updateTree()

    @Slot()
    def call_dkb_reader(self):
        self.results = sort_csvdata(self)
        self.saveResults(self.results)
        self.updateTree()

    @Slot()
    def test(self, item, column):
        Test = 1

    @Slot()
    def childCheckChanged(self, item, column):
        if column == 0:
            parent = item.parent()
            year = parent.text(0)
            month = item.text(1)
            if item.checkState(0) == QtCore.Qt.CheckState.Checked:
                value = 1
            else:
                value = 0
            print(str([year, month, value]))
            return [year, month, value]

    # @Slot()
    def updateTree(self):
        years = list(self.results.keys())
        for year in years:
            yearCheckbox = QtWidgets.QTreeWidgetItem()
            yearCheckbox.setText(0, str(year))
            self.mainTree.addTopLevelItem(yearCheckbox)
            months = list(self.results[year].keys())
            for month in months:
                monthCheckbox = QtWidgets.QTreeWidgetItem()
                monthCheckbox.setText(1, month)
                monthCheckbox.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                yearCheckbox.addChild(monthCheckbox)
        if not self.mainTree.isVisible():
            self.mainTree.setVisible(True)

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
            self.updateTree()
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

    def closeEvent(self, event):
        print('Application closed.')
        if os.path.isfile("data/lastResults.p"):
            currentDate = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            os.rename(r"data/lastResults.p", r"data/oldResults_" + currentDate + ".p")
            print('Files renamed.')


app = QtWidgets.QApplication(sys.argv)
widget = mainWidget()
widget.show()
sys.exit(app.exec_())
