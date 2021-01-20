from PySide2.QtCore import Qt, QDateTime
from PySide2 import QtWidgets

class MeterDialog(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(MeterDialog, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # nice widget for editing the date
        # self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime = QtWidgets.QDateEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        # Meter type - selector
        meterTypeLabel = QtWidgets.QLabel("Zähler")
        layout.addWidget(meterTypeLabel)
        self.meterTypeWidget = QtWidgets.QWidget(self)
        self.miniLayout = QtWidgets.QHBoxLayout(self.meterTypeWidget)
        self.meterTypeGrp = QtWidgets.QButtonGroup()
        self.electricity = QtWidgets.QCheckBox('Strom')
        self.electricity.setCheckState(Qt.CheckState.Checked)
        self.meterTypeGrp.addButton(self.electricity, 0)
        self.miniLayout.addWidget(self.electricity)
        self.gas = QtWidgets.QCheckBox('Gas')
        self.meterTypeGrp.addButton(self.gas, 1)
        self.miniLayout.addWidget(self.gas)
        self.water = QtWidgets.QCheckBox('Wasser')
        self.meterTypeGrp.addButton(self.water, 2)
        self.miniLayout.addWidget(self.water)
        layout.addWidget(self.meterTypeWidget)

        # level
        lvlLabel = QtWidgets.QLabel('Zählerstand')
        layout.addWidget(lvlLabel)
        self.lvlSpinBox = QtWidgets.QDoubleSpinBox()
        self.lvlSpinBox.setRange(0, 1000000)
        self.lvlSpinBox.setDecimals(3)
        # self.lvlSpinBox.setSuffix(' m^2')
        self.lvlSpinBox.setValue(0)
        layout.addWidget(self.lvlSpinBox)

        # OK and Cancel buttons
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
             Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        ## SIGNALS/SLOTS ##
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)


    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()


    # get meter type from dialog
    def mtrType(self):
        checkedID = self.meterTypeGrp.checkedId()
        if checkedID == 0:
            meterTyoe = 'Strom'
        elif checkedID == 1:
            meterTyoe = 'Gas'
        elif checkedID == 2:
            meterTyoe = 'Wasser'
        else:
            meterTyoe = '?'
        return meterTyoe


    # get level from spinBox
    def lvl(self):
        level = self.lvlSpinBox.value()
        return level


    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def doMeter(parent=None):
        dialog = MeterDialog(parent)
        result = dialog.exec_()
        dateData = dialog.dateTime().date()
        meterType = dialog.mtrType()
        level = dialog.lvl()

        dialogData = {
            'date': [dateData.year(), dateData.month(), dateData.day()],
            'result': result == QtWidgets.QDialog.Accepted,
            'meterTyoe': meterType,
            'level': level
        }
        return dialogData

# app = QtWidgets.QApplication([])
# # date, time, ok = MeterDialog.getDateTime()
# # print("{} {} {}".format(date, time, ok))
# dialogData = ManualEntryDialog.doManualEntry()
# print(dialogData)
# app.exec_()