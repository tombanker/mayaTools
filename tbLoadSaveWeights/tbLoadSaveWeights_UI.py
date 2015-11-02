import shiboken
from PySide import QtGui, QtCore
from functools import partial
import maya.OpenMayaUI as mui
import maya.cmds as cmds

def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    if pointer is not None:
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)

class tbLoadSaveWeights_UI(object):
    def __init__(self):
        self.moduleInstance = None
        self.UIElements = {}

        windowName = "tbLoadSaveWeightsWin"

        if cmds.window(windowName, exists=True):
            cmds.deleteUI(windowName)

        width = 295
        height = 210

        parent = getMayaWindow()
        window = QtGui.QMainWindow(parent)
        window.setObjectName(windowName)
        window.setWindowTitle("tbLoadSaveWeights")

        window.setFixedSize(width, height)

        mainWidget = QtGui.QWidget()
        window.setCentralWidget(mainWidget)

        # Main vertical layout
        verticalLayout = QtGui.QVBoxLayout(mainWidget)

        # File/directory UI elements
        directoryLayout = QtGui.QHBoxLayout()
        directoryLabel = QtGui.QLabel("Weights File:")
        self.directoryLineEdit = QtGui.QLineEdit()
        self.directoryLineEdit.setText(self.getSaveDirectory())
        self.directoryBtn = QtGui.QPushButton("...")
        self.directoryBtn.clicked.connect(partial(self.fileDialogWindow))

        verticalLayout.addLayout(directoryLayout)
        directoryLayout.addWidget(directoryLabel)
        directoryLayout.addWidget(self.directoryLineEdit)
        directoryLayout.addWidget(self.directoryBtn)

        # Main lab layout
        tabWidget = QtGui.QTabWidget()
        saveTab = QtGui.QWidget()
        tabWidget.addTab(saveTab, "Save Weights")
        loadTab = QtGui.QWidget()
        tabWidget.addTab(loadTab, "Load Weights")
        verticalLayout.addWidget(tabWidget)

        # Save tab UI elements
        skinClusterLabel = QtGui.QLabel("skinCluster:")
        skinClusterTransformLabel = QtGui.QLabel("Transform Node:")
        self.skinClusterTransformLineEdit = QtGui.QLineEdit()
        self.skinClusterTransformLineEdit.setEnabled(False)

        self.skinClusterComboBox = QtGui.QComboBox()
        self.setSkinClusterComboBoxText()
        self.setSkinclusterTransformNodeText()
        self.skinClusterComboBox.currentIndexChanged.connect(partial(self.setSkinclusterTransformNodeText))

        saveLabel = QtGui.QLabel("XML Format:")
        self.saveCheckBox = QtGui.QCheckBox("Human readable (slower save)")
        saveBtn = QtGui.QPushButton("Save")
        saveBtn.clicked.connect(partial(self.saveWeights))

        # Save tab layout
        saveTabLayout = QtGui.QVBoxLayout(saveTab)

        skinClusterTransformLayout = QtGui.QHBoxLayout()
        saveTabLayout.addLayout(skinClusterTransformLayout)
        skinClusterTransformLayout.addWidget(skinClusterTransformLabel)
        skinClusterTransformLayout.addWidget(self.skinClusterTransformLineEdit)

        skinClusterLayout = QtGui.QHBoxLayout()
        saveTabLayout.addLayout(skinClusterLayout)
        skinClusterLayout.addWidget(skinClusterLabel)
        skinClusterLayout.addWidget(self.skinClusterComboBox)

        saveLayout = QtGui.QHBoxLayout()
        saveTabLayout.addLayout(saveLayout)
        saveLayout.addWidget(saveLabel)
        saveLayout.addWidget(self.saveCheckBox)

        saveSpacer = QtGui.QSpacerItem(0, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        saveTabLayout.addItem(saveSpacer)

        saveHorizontalLine = QtGui.QFrame()
        saveHorizontalLine.setFrameShape(QtGui.QFrame.HLine)
        saveHorizontalLine.setFrameShadow(QtGui.QFrame.Sunken)
        saveTabLayout.addWidget(saveHorizontalLine)
        saveTabLayout.addWidget(saveBtn)

        # Load tab UI elements
        loadLabel = QtGui.QLabel("Transform Node:")
        self.loadLineEdit = QtGui.QLineEdit()
        self.loadLineEdit.setEnabled(False)
        self.setLoadLineEdit()
        self.setLoadTransformBtn = QtGui.QPushButton("<-- Mesh")
        self.setLoadTransformBtn.clicked.connect(partial(self.setLoadLineEdit))

        loadBtn = QtGui.QPushButton("Load")
        loadBtn.clicked.connect(partial(self.loadWeights))

        # Load tab layout
        loadTabLayout = QtGui.QVBoxLayout(loadTab)

        loadTransformLayout = QtGui.QHBoxLayout()
        loadTabLayout.addLayout(loadTransformLayout)

        loadTransformLayout.addWidget(loadLabel)
        loadTransformLayout.addWidget(self.loadLineEdit)
        loadTransformLayout.addWidget(self.setLoadTransformBtn)

        loadSpacer = QtGui.QSpacerItem(0, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        loadTabLayout.addItem(loadSpacer)

        loadHorizontalLine = QtGui.QFrame()
        loadHorizontalLine.setFrameShape(QtGui.QFrame.HLine)
        loadHorizontalLine.setFrameShadow(QtGui.QFrame.Sunken)
        loadTabLayout.addWidget(loadHorizontalLine)
        loadTabLayout.addWidget(loadBtn)

        window.show()

    def setLoadLineEdit(self, *args):
        sel = cmds.ls(sl=1)
        if len(sel):
            if  cmds.objectType(sel[0]) == "transform":
                self.loadLineEdit.setText(sel[0])
        else:
            self.loadLineEdit.setText("No mesh selected")

    def setSkinclusterTransformNodeText(self, *args):
        skinCluster = self.skinClusterComboBox.currentText()

        if str(self.skinClusterComboBox.currentText()) == "No skinCluster found":
            self.skinClusterTransformLineEdit.setText("No skinned mesh found")

        transformNode = cmds.listConnections(skinCluster, type='shape')

        if len(transformNode):
            self.skinClusterTransformLineEdit.setText(transformNode[0])

    def getSaveDirectory(self, *args):
        fileName = cmds.file(q=1, sceneName=1)
        workspace = cmds.workspace(q=1, fullName=1)

        if not len(fileName):
            return workspace
        else:
            return fileName.replace(".ma",".xml")

    def fileDialogWindow(self, *args):
        filePath = cmds.fileDialog2(cap="Specify a save weights file", fileFilter="*.xml",selectFileFilter="*.xml",
                              fileMode=0, okCaption="Select", cancelCaption="Cancel")[0]
        self.directoryLineEdit.setText(filePath)
        return filePath

    def setSkinClusterComboBoxText(self):
        skinClusters = cmds.ls(type="skinCluster")

        if len(skinClusters):
            for skinCluster in skinClusters:
                self.skinClusterComboBox.addItem(skinCluster)
        else:
            self.skinClusterComboBox.addItem("No skinCluster found")

    def getSkinClusterFromComboBox(self, *args):
        comboBoxText = str(self.skinClusterComboBox.currentText())
        if not len(comboBoxText):
            return None
        return comboBoxText

    def saveWeights(self, *args):
        import maya.mel as mel
        cmds.unloadPlugin('tbLoadSaveWeights.py')
        cmds.loadPlugin('tbLoadSaveWeights.py')
        mel.eval('tbLoadSaveWeights -a "export" -f "%s" -m "%s" -p %r'
                 % (self.directoryLineEdit.text(), self.skinClusterTransformLineEdit.text(), self.saveCheckBox.isChecked()))

    def loadWeights(self, *args):
        print '\n... loading weights'
        print 'file:', self.directoryLineEdit.text()
        print 'mesh:', self.loadLineEdit.text()
        import maya.mel as mel
        cmds.unloadPlugin('tbLoadSaveWeights.py')
        cmds.loadPlugin('tbLoadSaveWeights.py')
        mel.eval('tbLoadSaveWeights -a "import" -f "%s" -m "%s"'
                 % (self.directoryLineEdit.text(), self.skinClusterTransformLineEdit.text()))

if __name__ == "__main__":
    tbLoadSaveWeights_UI()