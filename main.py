# This Python file uses the following encoding: utf-8
import sys


from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from widgets.mainWidget import MainWidget


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    widget = MainWidget()
    widget.show()
    sys.exit(app.exec_())
