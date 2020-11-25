# This Python file uses the following encoding: utf-8
import os


from PySide2.QtWidgets import QWidget, QFileDialog, QPushButton, QTextEdit
from PySide2.QtCore import QFile, QDir
from PySide2.QtUiTools import QUiLoader
from dkbReader import sort_csvdata


class widgetWindow(QWidget):
    def __init__(self):
        super(widgetWindow, self).__init__()
        self.load_ui()
        self.collectChildren()
        self.csvSearchButton.clicked.connect(self.find_csv_file)
        self.resultsButton.clicked.connect(self.call_dkb_reader)

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

    def collectChildren(self):
        self.csvSearchButton = self.findChildren(QPushButton, 'csvSearchButton')[0]
        self.resultsButton = self.findChildren(QPushButton, 'resultsButton')[0]
        self.pathText = self.findChildren(QTextEdit, 'pathText')[0]

    def find_csv_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            QDir().home().path() + '/Downloads', "CSV (*.csv)")
        self.pathText.setText(fname[0])

    def call_dkb_reader(self):
        results = sort_csvdata(self)
        test = 1