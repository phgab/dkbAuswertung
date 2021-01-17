from PySide2.QtCore import Qt, QDateTime
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot
from functions.dkbReader import getCatSpe, getCatInc

#TODO: change. everyting.

class ManualEntryDialog(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(ManualEntryDialog, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # nice widget for editing the date
        # self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime = QtWidgets.QDateEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        # Income/spending - selector
        incSpeLabel = QtWidgets.QLabel("Einnahme / Ausgabe")
        layout.addWidget(incSpeLabel)
        self.incSpeWidget = QtWidgets.QWidget(self)
        self.miniLayout = QtWidgets.QHBoxLayout(self.incSpeWidget)
        self.incSpeBoxGrp = QtWidgets.QButtonGroup()
        self.spending = QtWidgets.QCheckBox('Ausgaben')
        self.spending.setCheckState(Qt.CheckState.Checked)
        self.incSpeBoxGrp.addButton(self.spending, 0)
        self.miniLayout.addWidget(self.spending)
        self.income = QtWidgets.QCheckBox('Einnahmen')
        self.incSpeBoxGrp.addButton(self.income, 1)
        self.miniLayout.addWidget(self.income)
        self.meter = QtWidgets.QCheckBox('Zählerstand')
        self.incSpeBoxGrp.addButton(self.meter, 2)
        self.miniLayout.addWidget(self.meter)
        layout.addWidget(self.incSpeWidget)

        # Item name
        nameLabel = QtWidgets.QLabel('Bezeichnung')
        layout.addWidget(nameLabel)
        self.nameText = QtWidgets.QTextEdit("")
        self.nameText.setMaximumHeight(60)
        self.nameText.setMinimumWidth(300)
        layout.addWidget(self.nameText)

        # Amount
        amtLabel = QtWidgets.QLabel('Summe')
        layout.addWidget(amtLabel)
        self.amtSpinBox = QtWidgets.QDoubleSpinBox()
        self.amtSpinBox.setRange(0, 100000)
        self.amtSpinBox.setDecimals(2)
        self.amtSpinBox.setSuffix(' €')
        self.amtSpinBox.setValue(0)
        layout.addWidget(self.amtSpinBox)

        # Category combo box
        catLabel = QtWidgets.QLabel('Kategorie')
        layout.addWidget(catLabel)
        self.catSelection = QtWidgets.QComboBox()
        choices = getCatSpe()
        choices.pop(-1)
        self.catChoices = choices
        for cat in self.catChoices:
            self.catSelection.addItem(cat)
        layout.addWidget(self.catSelection)

        # 'Sonstiges' specifier
        self.catIdentLabel = QtWidgets.QLabel('Spezifikation')
        layout.addWidget(self.catIdentLabel)
        self.catIdentText = QtWidgets.QTextEdit("")
        self.catIdentText.setMaximumHeight(30)
        self.catIdentText.setMinimumWidth(300)
        layout.addWidget(self.catIdentText)
        self.catIdentLabel.setVisible(False)
        self.catIdentText.setVisible(False)

        # OK and Cancel buttons
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
             Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        ## SIGNALS/SLOTS ##
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.incSpeBoxGrp.idClicked.connect(self.setSelectionContent)
        self.catSelection.currentIndexChanged.connect(self.catchMisc)

    
    # set appropriate categories for the selection
    @Slot()
    def setSelectionContent(self, checkedID):
        #checkedID = self.incSpeBoxGrp.checkedId()
        self.catSelection.clear()
        # check selected type
        if checkedID == 0:
            choices = getCatSpe()
            choices.pop(-1)
            self.catChoices = choices
            # self.catChoices[-1].pop()
        elif checkedID == 1:
            choices = getCatInc()
            choices.pop(-1)
            self.catChoices = choices
        elif checkedID == 2:
            self.catChoices = ['Strom', 'Gas', 'Wasser']
        else:
            self.catChoices = []
        # add categories
        for cat in self.catChoices:
            self.catSelection.addItem(cat)


    # catch 'Sonstiges'
    @Slot()
    def catchMisc(self, idx):
        category = self.catSelection.currentText()
        if category == 'Sonstiges':
            self.catIdentLabel.setVisible(True)
            self.catIdentText.setVisible(True)
        else:
            self.catIdentLabel.setVisible(False)
            self.catIdentText.setVisible(False)


    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()


    # get income / spending from dialog
    def incSpe(self):
        checkedID = self.incSpeBoxGrp.checkedId()
        if checkedID == 0:
            incSpeStatus = 'Ausgaben'
        elif checkedID == 1:
            incSpeStatus = 'Einnahmen'
        else:
            incSpeStatus = '?'
        return incSpeStatus


    # get amount from spinBox
    def amt(self):
        amount = self.amtSpinBox.value()
        return amount


    # get description
    def descr(self):
        description = self.nameText.toPlainText()
        return description


    # get category
    def cat(self):
        category = self.catSelection.currentText()
        return category


    # get misc category identifier
    def catIdent(self):
        if self.catIdentLabel.isVisible:
            catIdentText = self.catIdentText.toPlainText()
        else:
            catIdentText = ''
        return catIdentText


    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = ManualEntryDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return (date.date(), date.time(), result == QtWidgets.QDialog.Accepted)


    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def doManualEntry(parent=None):
        dialog = ManualEntryDialog(parent)
        result = dialog.exec_()
        dateData = dialog.dateTime().date()
        incSpe = dialog.incSpe()
        amt = dialog.amt()
        descr = dialog.descr()
        cat = dialog.cat()
        catIdent = dialog.catIdent()

        dialogData = {
            'date': [dateData.year(), dateData.month(), dateData.day()],
            'result': result == QtWidgets.QDialog.Accepted,
            'incSpe': incSpe,
            'amt': amt,
            'descr': descr,
            'cat': cat,
            'catIdent': catIdent
        }
        return dialogData

# app = QtWidgets.QApplication([])
# # date, time, ok = ManualEntryDialog.getDateTime()
# # print("{} {} {}".format(date, time, ok))
# dialogData = ManualEntryDialog.doManualEntry()
# print(dialogData)
# app.exec_()