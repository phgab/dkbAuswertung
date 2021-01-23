import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
from PySide2.QtCore import QPoint, Qt, QDateTime, QDate
from PySide2.QtGui import QPainter, QFont
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCharts import QtCharts
import pickle
import math


class PlotWidget(QtCharts.QChartView):
    sgn_redrawPlot = Signal()
    sgn_updatePlot = Signal()
    sgn_updateLegendSelection = Signal(list)

    def __init__(self, parent=None):
        QtCharts.QChartView.__init__(self, parent)
        self.results = None
        self.selection = None
        self.plotData = None
        self.meterData = None
        self.plotDataTags = None
        self.catList = None
        self.meterList = None
        self.sumData = None
        self.barSets = None
        self.currentPlot = 0
        self.currentLegendPlot = None

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


    @Slot()
    def plotSelector(self, plotNr):
        self.currentPlot = plotNr
        self.currentLegendPlot = None
        self.redrawPlot()
        # print('Plot no. ' + str(plotNr) + ' selected.')

    @Slot()
    def legendSelector(self, legendText):
        self.currentLegendPlot = legendText
        self.redrawPlot()
        # print('Plot no. ' + str(plotNr) + ' selected.')


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
        newData = {cat: [] for cat in catList}
        dataTags = []
        for year in list(self.selection.keys()):
            for month in list(self.selection[year].keys()):
                if not self.selection[year][month]:
                    continue
                for cat in catList:
                    if cat == "Zählerstände":
                        if cat in self.results[int(year)][month]:
                            # first encounter
                            if not newData[cat]:
                                newData[cat] = {}
                            for meterType in list(self.results[int(year)][month][cat].keys()):
                                if meterType not in newData[cat]:
                                    newData[cat][meterType] = []
                                for bch in self.results[int(year)][month][cat][meterType]["bch"]:
                                    date = QDateTime()
                                    date.setDate(QDate(bch['Ablesung_Jahr'], bch['Ablesung_Monat'], bch['Ablesung_Tag']))
                                    level = bch['Zählerstand']
                                    newData[cat][meterType].append({'level': level, 'date': date})
                    elif cat in self.results[int(year)][month]:
                        if 'sum' in self.results[int(year)][month][cat]:
                            newData[cat].append(self.results[int(year)][month][cat]['sum'])
                        else:
                            newData[cat].append(sum([self.results[int(year)][month][cat][catIdent]['sum']
                                                     for catIdent in self.results[int(year)][month][cat]]))
                    else:
                        newData[cat].append(0)
                dataTags.append(month + ' ' + year)

        numTags = len(dataTags)
        newSumData = {'exp': [0]*numTags, 'inc': [0]*numTags, 'sav': [0]*numTags}
        for idx in range(numTags):
            for cat in list(newData.keys()):
                if cat == "Einnahmen":
                    newSumData['inc'][idx] += newData[cat][idx]
                elif cat == "Zählerstände":
                    continue
                else:
                    newSumData['exp'][idx] += newData[cat][idx]
            if idx == 0:
                newSumData['sav'][idx] = newSumData['inc'][idx] - newSumData['exp'][idx]
            else:
                newSumData['sav'][idx] = newSumData['sav'][idx-1] + newSumData['inc'][idx] - newSumData['exp'][idx]

        self.plotData = newData
        self.plotDataTags = dataTags
        self.sumData = newSumData


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

        if self.currentPlot == 0:
            if self.currentLegendPlot is None or self.currentLegendPlot == 'Alle':
                self.plotAllExpenseBars()
            else:
                self.plotAllExpenseBars(self.currentLegendPlot)
        elif self.currentPlot == 1:
            self.currentLegendPlot = None
            self.plotSavingsBars()
        elif self.currentPlot == 2:
            if 'Zählerstände' in self.plotData.keys():
                meterList = [meterType for meterType in self.plotData['Zählerstände'].keys()]
                meterListChanged = False
                if not self.meterList == meterList:
                    self.meterList = meterList
                    meterListChanged = True
                if self.currentLegendPlot is None or meterListChanged:
                    self.sgn_updateLegendSelection.emit(self.meterList)
                    self.currentLegendPlot = meterList[0]
                self.plotMeterAvg(self.currentLegendPlot)

        else:
            print('Invalid plot no. selected - nothing is drawn')


    def plotAllExpenseBars(self, legendPlot=None):
        chart = QtCharts.QChart()

        barSets = []
        barSeries = QtCharts.QBarSeries()
        maxVal = 0
        if legendPlot is None:
            catList = ['Alle']
            for cat in list(self.plotData.keys()):
                if cat == "Einnahmen" or cat == "Zählerstände":
                    continue
                barSet = QtCharts.QBarSet(cat)
                barSet.append(self.plotData[cat])
                barSets.append(barSet)
                barSeries.append(barSet)
                catList.append(cat)
                maxVal = max(maxVal, max(self.plotData[cat]))
            self.barSets = barSets
            self.catList = catList
        else:
            barSet = QtCharts.QBarSet(legendPlot)
            barSet.append(self.plotData[legendPlot])
            barSets.append(barSet)
            barSeries.append(barSet)
            maxVal = max(self.plotData[legendPlot])

        chart.addSeries(barSeries)

        titleFont = QFont("Sans Serif")
        titleFont.setPointSize(16)
        titleFont.setBold(True)
        chart.setTitleFont(titleFont)
        if legendPlot is None:
            chart.setTitle("Ausgaben")
        else:
            chart.setTitle("Ausgaben: " + legendPlot)

        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(self.plotDataTags)
        chart.setAxisX(axisX, barSeries)
        # axisX.setRange(self.plotDataTags[0], self.plotDataTags[-1])

        axisY = QtCharts.QValueAxis()
        axisY.setLabelFormat("%i")
        axisY.setTitleText("€")
        self.setYRange(maxVal, axisY)
        # chart.setAxisY(axisY, lineSeries)
        chart.setAxisY(axisY, barSeries)
        # axisY.setRange(0, 20)

        if legendPlot is None:
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)
        else:
            chart.legend().setVisible(False)

        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        if legendPlot is None:
            self.sgn_updateLegendSelection.emit(self.catList)
        # draw the plot from scratch (if that makes a difference)
        print('Expense bar plot drawn')

    def plotSavingsBars(self):
        chart = QtCharts.QChart()

        # barSets = []
        maxVal = 0
        minVal = 0
        barSeries = QtCharts.QBarSeries()
        expSet = QtCharts.QBarSet('Ausgaben')
        expSet.append(self.sumData['exp'])
        maxVal = max(maxVal, max(self.sumData['exp']))
        minVal = min(minVal, min(self.sumData['exp']))
        barSeries.append(expSet)

        incSet = QtCharts.QBarSet('Einnahmen')
        incSet.append(self.sumData['inc'])
        maxVal = max(maxVal, max(self.sumData['inc']))
        minVal = min(minVal, min(self.sumData['inc']))
        barSeries.append(incSet)

        savSet = QtCharts.QBarSet('Rücklagen')
        savSet.append(self.sumData['sav'])
        maxVal = max(maxVal, max(self.sumData['sav']))
        minVal = min(minVal, min(self.sumData['sav']))
        barSeries.append(savSet)

        # self.barSets = barSets

        chart.addSeries(barSeries)
        titleFont = QFont("Sans Serif")
        titleFont.setPointSize(16)
        titleFont.setBold(True)

        chart.setTitleFont(titleFont)
        chart.setTitle("Rücklagen")

        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(self.plotDataTags)
        chart.setAxisX(axisX, barSeries)
        # axisX.setRange(self.plotDataTags[0], self.plotDataTags[-1])

        axisY = QtCharts.QValueAxis()
        axisY.setLabelFormat("%i")
        axisY.setTitleText("€")
        if minVal < 0:
            self.setYRange(maxVal, axisY, minVal)
        else:
            self.setYRange(maxVal, axisY)
        # chart.setAxisY(axisY, lineSeries)
        chart.setAxisY(axisY, barSeries)
        # axisY.setRange(0, 20)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        # draw the plot from scratch (if that makes a difference)
        print('Expense bar plot drawn')


    def plotMeterAvg(self, legendSelection):
        print(legendSelection)


    @Slot()
    def updatePlot(self):
        #only change plot parameters, not the underlying data
        test=1


    def setYRange(self, maxY, axisY: QtCharts.QValueAxis(), minY=None):
        if maxY <= 60:
            divider = 10
        elif maxY <= 200:
            divider = 50
        elif maxY <= 600:
            divider = 100
        elif maxY <= 2000:
            divider = 500
        elif maxY <= 6000:
            divider = 1000
        elif maxY <= 20000:
            divider = 5000

        axisY.applyNiceNumbers()

        rangeLim = math.ceil(maxY / divider) * divider
        if minY is None:
            axisY.setRange(0, rangeLim)
        else:
            rangeMin = math.floor(minY / divider) * divider
            axisY.setRange(rangeMin, rangeLim)

        if minY is None:
            numTicks = math.ceil(maxY / divider) + 1
        else:
            numTicks = math.ceil(maxY / divider) + 1 - math.floor(minY / divider)
        axisY.setTickCount(numTicks)



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


    def sortCats(self, text):
        try:
            orderList = pickle.load(open("data/catOrderList.p", "rb"))
            for num, cat in enumerate(orderList):
                if text == cat:
                    return str(num)
            return str(len(orderList)) + text[0:3]
        except:
            return text


    def computeExpenseSums(self):
        test = 1

    def computeSavings(self):
        test = 1