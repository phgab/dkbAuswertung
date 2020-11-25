# This Python file uses the following encoding: utf-8
import sys


from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from window import widgetWindow


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    widget = widgetWindow()
    widget.show()
    sys.exit(app.exec_())
