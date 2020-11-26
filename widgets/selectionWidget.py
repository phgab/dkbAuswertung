from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot

class SelectionWidget(QtWidgets.QWidget):
    checkboxChanged = Signal(dict)
    treeUpdated = Signal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.selection = None

        ## TREE VIEW WIDGETS ##
        mainTree = QtWidgets.QTreeWidget()
        mainTree.setHeaderLabels(["Jahr", "Monat"])
        mainTree.setVisible(False)
        mainTree.setMinimumHeight(200)
        mainTree.setMaximumWidth(300)
        # mainTree.setMaximumHeight(1000)
        self.mainTree = mainTree

        self.mergeButton = QtWidgets.QPushButton("Gesamtdaten ergänzen")
        self.mergeButton.setMaximumWidth(300)
        self.mergeButton.setVisible(False)

        ## SIGNALS / SLOTS
        mainTree.itemChanged.connect(self.childCheckChanged)

        ## LAYOUT ##
        # Do I Really need to do this?!
        treeLayout = QtWidgets.QVBoxLayout()
        treeLayout.addWidget(self.mergeButton)
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
        if not self.mergeButton.isVisible():
            if not all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                self.mergeButton.setVisible(True)
        else:
            if all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                self.mergeButton.setVisible(False)

        self.treeUpdated.emit()

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
            if not self.mergeButton.isVisible():
                if not all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                    self.mergeButton.setVisible(True)
            else:
                if all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                    self.mergeButton.setVisible(False)

            self.checkboxChanged.emit(self.selection)
            # return [year, month, value]


    def sortMonths(self, str):
        order = ["Januar", "Februar", "März", "April",
                 "Mai", "Juni", "Juli", "August",
                 "September", "Oktober", "November", "Dezember"]
        for num, month in enumerate(order):
            if str == month:
                return num
