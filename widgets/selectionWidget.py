from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot

class SelectionWidget(QtWidgets.QWidget):
    checkboxChanged = Signal(dict)
    treeUpdated = Signal()
    doMerge = Signal(dict)

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

        self.plotSelection = QtWidgets.QComboBox()
        self.plotChoices = ['Ausgaben: Kategorien', 'Rücklagen', 'Zählerstände', 'Verbrauch']#, 'Ausgaben vs. Einnahmen', 'Ausgaben: Sonstiges']
        for plot in self.plotChoices:
            self.plotSelection.addItem(plot)
        self.plotSelection.setMaximumWidth(300)
        self.plotSelection.setVisible(False)

        self.legendSelection = QtWidgets.QComboBox()
        self.legendSelection.setMaximumWidth(200)
        self.legendSelection.setVisible(False)

        ## SIGNALS / SLOTS
        mainTree.itemChanged.connect(self.childCheckChanged)
        self.mergeButton.clicked.connect(self.initiateMerge)
        self.plotSelection.currentIndexChanged.connect(self.plotSelChanged)

        ## LAYOUT ##
        # Do I Really need to do this?!
        treeLayout = QtWidgets.QVBoxLayout()
        treeLayout.addWidget(self.mergeButton)
        treeLayout.addWidget(mainTree)
        treeLayout.addWidget(self.plotSelection)
        treeLayout.addWidget(self.legendSelection)
        self.setLayout(treeLayout)


    @Slot()
    def test(self, item, column):
        Test = 1


    @Slot()
    def updateTree(self, results):
        # To ease writing further on
        checkDict = {False: QtCore.Qt.CheckState.Unchecked, True: QtCore.Qt.CheckState.Checked, 3: QtCore.Qt.CheckState.PartiallyChecked}

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
                    if month not in newSelect[year] or \
                            month in newSelect[year] and newSelect[year][month] == self.selection[year][month]:
                        continue
                    else:
                        newSelect[year][month] = self.selection[year][month]
        self.selection = newSelect

        self.mainTree.clear()
        years = list(self.selection.keys())
        for year in years:
            yearCheckbox = QtWidgets.QTreeWidgetItem()
            yearCheckbox.setText(0, year)
            yearCheckbox.setCheckState(0, checkDict[False])
            # yearCheckbox.setFlags(QtCore.Qt.ItemIsAutoTristate)
            yearCheckbox.setFlags(yearCheckbox.flags() | QtCore.Qt.ItemIsAutoTristate | QtCore.Qt.ItemIsUserCheckable)
            # yearCheckbox.setTristate(True)
            if all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                yearCheckbox.setCheckState(0, checkDict[False])
            elif not all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                yearCheckbox.setCheckState(0, checkDict[True])
            else:
                test = 1
                # yearCheckbox.setCheckState(0, checkDict[3])

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
                self.plotSelection.setVisible(True)
                if self.plotSelection.currentIndex() == 0:
                    self.legendSelection.setVisible(True)
                else:
                    self.legendSelection.setVisible(False)
        else:
            if all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                self.mergeButton.setVisible(False)
                self.plotSelection.setVisible(False)
                self.legendSelection.setVisible(False)

        self.treeUpdated.emit()

    @Slot()
    def childCheckChanged(self, item, column):
        if column == 0:
            parent = item.parent()
            if parent is None:
                # if not item.checkState(0) == QtCore.Qt.CheckState.PartiallyChecked:
                #     self.checkboxChanged.emit(self.selection)
                return
            year = parent.text(0)
            month = item.text(1)
            if item.checkState(0) == QtCore.Qt.CheckState.Checked:
                value = True
            else:
                value = False
            if month == '':
                test = 1
            else:
                self.selection[year][month] = value

            # print(str([year, month, value]))
            if not self.mergeButton.isVisible():
                if not all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                    self.mergeButton.setVisible(True)
                    self.plotSelection.setVisible(True)
                    self.legendSelection.setVisible(True)
            else:
                if all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
                    self.mergeButton.setVisible(False)
                    self.plotSelection.setVisible(False)
                    self.legendSelection.setVisible(False)

            if not parent.checkState(0) == QtCore.Qt.CheckState.PartiallyChecked:
                state = item.checkState(0)
                if not all([state == childstate for childstate in [parent.child(idx).checkState(0) for idx in range(parent.childCount())]]):
                    return

            self.checkboxChanged.emit(self.selection)
            # return [year, month, value]


    def sortMonths(self, str):
        order = ["Januar", "Februar", "März", "April",
                 "Mai", "Juni", "Juli", "August",
                 "September", "Oktober", "November", "Dezember"]
        for num, month in enumerate(order):
            if str == month:
                return num


    @Slot()
    def initiateMerge(self):
        self.doMerge.emit(self.selection)


    @Slot()
    def updateLegendSelCont(self, catList):
        self.legendSelection.blockSignals(True)
        self.legendSelection.clear()
        for cat in catList:
            self.legendSelection.addItem(cat)
        self.legendSelection.blockSignals(False)


    @Slot()
    def plotSelChanged(self, plotNr):
        if (plotNr == 0 or plotNr == 2 or plotNr == 3) and self.plotSelection.isVisible():
            self.legendSelection.setVisible(True)
        else:
            self.legendSelection.setVisible(False)