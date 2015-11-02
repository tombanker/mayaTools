from PySide import QtGui, QtCore, QtUiTools
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

UI_FILE_PATH = 'c:/Users/Tom/PycharmProjects/tb_ribbon/ribbonLimbUI.ui'

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr),QtGui.QWidget)

class ribbonLimbMainWindow(object):
    def __init__(self):
        self.MainWindow = None

    def loadUiWidget(self, uiFileName, parent=getMayaWindow()):
        loader = QtUiTools.QUiLoader()
        uiFile = QtCore.QFile(uiFileName)
        uiFile.open(QtCore.QFile.ReadOnly)
        ui = loader.load(uiFile, parent)
        return ui

    def connectSignals(self):
        self.MainWindow.applyButton.clicked.connect(partial(self.applySignalMethod))
        self.MainWindow.closeButton.clicked.connect(partial(self.closeSignalMethod))

    def applySignalMethod(self, *args):
        import core
        name = self.MainWindow.nameLineEdit.text()
        numJnts = int(self.MainWindow.numJointsLineEdit.text())
        width = float(self.MainWindow.widthLineEdit.text())
        lengthRatio = float(self.MainWindow.lengthRatioLineEdit.text())
        setupCons = self.MainWindow.createFkControlsCheckBox.isChecked()
        core.RibbonLimb(name, numJnts, width, lengthRatio, setupCons)

    def closeSignalMethod(self, *args):
        self.close()

    def close(self):
        if self.MainWindow is not None:
            self.MainWindow.close()
            self.MainWindow = None

    def show(self):
        self.close()
        app = QtGui.QApplication.instance()
        self.MainWindow = self.loadUiWidget(UI_FILE_PATH)
        self.connectSignals()
        self.MainWindow.show()
        app.exec_()

ribbonLimbMainWindow().show()