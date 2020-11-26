import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCharts import QtCharts
import datetime
import pickle


class PlotWidget(QtCharts.QChartView):
    sgn_redrawPlot = Signal()
    sgn_updatePlot = Signal()

    def __init__(self, parent=None):
        QtCharts.QChartView.__init__(self, parent)
        self.results = None
        self.selection = None
        self.plotData = None
        self.plotDataTags = None
        self.barSets = None

        self.setMinimumWidth(600)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setVisible(False)
        self.sgn_redrawPlot.connect(self.redrawPlot)


    @Slot()
    def updateData(self, results, selection):
        self.results = results
        self.selection = selection
        self.createDatasets()
        self.sgn_redrawPlot.emit()

    @Slot()
    def updateSelection(self, selection):
        self.selection = selection
        self.createDatasets()
        self.sgn_redrawPlot.emit()


    def createDatasets(self):
        if self.results is None:
            print('No results - no data is calculated')
            if self.isVisible():
                self.setVisible(False)
            return
        elif self.selection is None:
            print('No selection - no data is calculated')
            if self.isVisible():
                self.setVisible(False)
            return
        elif all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
            print('Nothing selected - no data is calculated')
            if self.isVisible():
                self.setVisible(False)
            return
        # If no interrupt, set visible
        if not self.isVisible():
            self.setVisible(True)

        catList = self.findCategories(self.results)
        newData = {cat:[] for cat in catList}
        dataTags = []
        for year in list(self.selection.keys()):
            for month in list(self.selection[year].keys()):
                if not self.selection[year][month]:
                    continue
                for cat in catList:
                    if cat in self.results[int(year)][month]:
                        if 'sum' in self.results[int(year)][month][cat]:
                            newData[cat].append(self.results[int(year)][month][cat]['sum'])
                        else:
                            newData[cat].append(sum([self.results[int(year)][month][cat][catIdent]['sum']
                                                     for catIdent in self.results[int(year)][month][cat]]))
                    else:
                        newData[cat].append(0)
                dataTags.append(month + ' ' + year)
        self.plotData = newData
        self.plotDataTags = dataTags


    @Slot()
    def redrawPlot(self):
        if self.results is None:
            print('No results - nothing is drawn')
            return
        elif self.selection is None:
            print('No selection - nothing is drawn')
            return
        elif all([self.selection[year][mon] == 0 for year in self.selection for mon in self.selection[year]]):
            print('Nothing selected - nothing is drawn')
            return

        chart = QtCharts.QChart()

        barSets = []
        barSeries = QtCharts.QBarSeries()
        for cat in list(self.plotData.keys()):
            set = QtCharts.QBarSet(cat)
            set.append(self.plotData[cat])
            barSets.append(set)
            barSeries.append(set)
        self.barSets = barSets

        chart.addSeries(barSeries)
        chart.setTitle("Ausgaben")
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(self.plotDataTags)
        chart.setAxisX(axisX, barSeries)
        #axisX.setRange(self.plotDataTags[0], self.plotDataTags[-1])

        axisY = QtCharts.QValueAxis()
        # chart.setAxisY(axisY, lineSeries)
        chart.setAxisY(axisY, barSeries)
        #axisY.setRange(0, 20)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        # draw the plot from scratch (if that makes a difference)

    @Slot()
    def updatePlot(self):
        #only change plot parameters, not the underlying data
        test=1


    def findCategories(self, results):
        if results is None:
            print('No results - no categories found')
            return []
        catSet = set()
        for year in list(results.keys()):
            for month in list(results[year].keys()):
                for cat in list(results[year][month].keys()):
                    if not cat == "Einnahmen":
                        catSet.add(cat)
        catList = sorted(list(catSet), key=self.sortCats)
        return catList


    def sortCats(self, str):
        try:
            orderList = pickle.load("data/catOrderList.p", "rb")
            for num, cat in enumerate(orderList):
                if str == cat:
                    return num
            return len(orderList)
        except:
            return str
