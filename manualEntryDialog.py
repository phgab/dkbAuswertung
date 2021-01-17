from PySide2.QtCore import Qt, QDateTime
from PySide2 import QtWidgets

#TODO: change. everyting.

class ManualEntryDialog(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(ManualEntryDialog, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # nice widget for editing the date
        self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        # Income/spending - selector
        incSpeLabel = QtWidgets.QLabel("Pfad")
        layout.addWidget(incSpeLabel)
        miniLayout = QtWidgets.QHBoxLayout(self)
        self.incSpeBoxGrp = QtWidgets.QButtonGroup()
        self.spending = QtWidgets.QCheckBox('Ausgaben')
        self.incSpeBoxGrp.addButton(self.spending, 0)
        miniLayout.addWidget(self.spending)
        self.income = QtWidgets.QCheckBox('Einnahmen')
        self.incSpeBoxGrp.addButton(self.income, 1)
        miniLayout.addWidget(self.income)
        layout.addWidget(miniLayout)

        # Item name
        nameLabel = QtWidgets.QLabel('Bezeichnung')
        layout.addWidget(nameLabel)
        self.nameText = QtWidgets.QTextEdit("")
        layout.addWidget(self.nameText)

        # Category combo box


        # OK and Cancel buttons
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
             Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = ManualEntryDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return (date.date(), date.time(), result == QtWidgets.QDialog.Accepted)

app = QtWidgets.QApplication([])
date, time, ok = ManualEntryDialog.getDateTime()
print("{} {} {}".format(date, time, ok))
app.exec_()