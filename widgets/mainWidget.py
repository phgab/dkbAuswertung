import os
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot
import datetime
from widgets.fileWidget import FileWidget
from widgets.selectionWidget import SelectionWidget
from widgets.plotWidget import PlotWidget
import shutil


class MainWidget(QtWidgets.QWidget):
    updatePlotData = Signal(dict, dict)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.fileWidget = FileWidget()
        self.selectionWidget = SelectionWidget()
        self.plotWidget = PlotWidget()

        ## LAYOUT ##
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(self.fileWidget, 0, 0)
        gridLayout.addWidget(self.selectionWidget, 1, 0)
        gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(gridLayout, 3)
        mainLayout.addWidget(self.plotWidget, 7)
        self.setLayout(mainLayout)

        ## SIGNALS / SLOTS ##
        self.fileWidget.updateTree.connect(self.selectionWidget.updateTree)
        self.selectionWidget.treeUpdated.connect(self.transferPlotData)
        self.updatePlotData.connect(self.plotWidget.updateData)
        self.selectionWidget.checkboxChanged.connect(self.plotWidget.updateSelection)
        self.selectionWidget.plotSelection.currentIndexChanged.connect(self.plotWidget.plotSelector)
        self.selectionWidget.doMerge.connect(self.fileWidget.mergeResults)
        self.plotWidget.sgn_updateLegendSelection.connect(self.selectionWidget.updateLegendSelCont)
        self.selectionWidget.legendSelection.currentTextChanged.connect(self.plotWidget.legendSelector)


    @Slot()
    def transferPlotData(self):
        self.updatePlotData.emit(self.fileWidget.results, self.selectionWidget.selection)


    def closeEvent(self, event):
        print('Application closed.')
        if os.path.isfile("data/lastResults.p"):
            currentDate = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            shutil.copy2("data/lastResults.p", "data/archive/oldResults_" + currentDate + ".p")
            # os.rename(r"data/lastResults.p", r"data/oldResults_" + currentDate + ".p")
            print('Files renamed.')
