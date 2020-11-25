import os
from PySide2 import QtWidgets
import datetime
from widgets.fileWidget import FileWidget
from widgets.selectionWidget import SelectionWidget
from widgets.plotWidget import PlotWidget



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
