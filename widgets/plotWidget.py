import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtCharts import QtCharts
import datetime
import pickle


class PlotWidget(QtCharts.QChartView):

    def __init__(self, parent=None):
        QtCharts.QChartView.__init__(self, parent)
        self.results = None
        self.selection = None


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

        set0 = QtCharts.QBarSet("Jane")
        barSeries = QtCharts.QBarSeries()
        barSeries.append(set0)

        chart.addSeries(barSeries)
        chart.setTitle("Line and barchart example")
        categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        # chart.setAxisX(axisX, lineSeries)
        chart.setAxisX(axisX, barSeries)
        axisX.setRange("Jan", "Jun")

        axisY = QtCharts.QValueAxis()
        # chart.setAxisY(axisY, lineSeries)
        chart.setAxisY(axisY, barSeries)
        axisY.setRange(0, 20)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

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
