from PySide import QtGui, QtCore
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from functools import partial

class Node(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.children = []
        self.parent = parent

        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        if cmds.objExists(self.name):
            return cmds.objectType(self.name)
        return "NODE"

    def addChild(self, child):
        self.children.append(child)

    def name(self):
        return self.name

    def setName(self, name):
        self.name = name

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def parent(self):
        return self.parent

    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)

    def log(self, tabLevel=-1):
        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "/------" + self.name + "\n"

        for child in self.children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"
        return output

class SceneGraphModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(SceneGraphModel, self).__init__(parent)
        self.rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name
            else:
                return node.typeInfo()

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo =  node.typeInfo()

                iconType = QtGui.QPixmap(":/"+typeInfo+".svg")
                return QtGui.QIcon(iconType)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(value)
                return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Object"
            else:
                return "Type Info"

    def flags(self, index):
        # return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        node = index.internalPointer()
        parentNode = node.parent

        if parentNode == self.rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()

        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def itemFromIndex(self, index):
        return index.internalPointer().name

def getMayaWindow():
    pointer = omui.MQtUtil.mainWindow()
    if pointer is not None:
        return wrapInstance(long(pointer), QtGui.QWidget)

class SearchSceneUI(object):
    def __init__(self):
        rootNode = Node("root")
        model = SceneGraphModel(rootNode)

        dagNodes = sorted(cmds.ls())
        for dagNode in cmds.ls():
            childNode = Node(dagNode, rootNode)

        windowName = "windowObjectName"

        if cmds.window(windowName, exists=True):
            cmds.deleteUI(windowName)

        parentWindow = getMayaWindow()
        mainWindow = QtGui.QMainWindow(parentWindow)
        mainWindow.setObjectName(windowName)
        mainWindow.setWindowTitle("windowTitle")
        mainWidget = QtGui.QWidget()
        mainWindow.setCentralWidget(mainWidget)
        mainLayout = QtGui.QVBoxLayout(mainWidget)

        topLayout = QtGui.QHBoxLayout()
        nameLabel = QtGui.QLabel("Name:")
        self.nameLineEdit = QtGui.QLineEdit()
        typeLabel = QtGui.QLabel("Type:")
        self.typeLineEdit = QtGui.QLineEdit()

        mainLayout.addLayout(topLayout)
        topLayout.addWidget(nameLabel)
        topLayout.addWidget(self.nameLineEdit)
        topLayout.addWidget(typeLabel)
        topLayout.addWidget(self.typeLineEdit)

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSourceModel(model)

        treeView = QtGui.QTreeView(parent=getMayaWindow())
        treeView.setWindowFlags(QtCore.Qt.Window)
        treeView.setModel(self.proxyModel)
        treeView.resizeColumnToContents(0)
        treeView.setFont(QtGui.QFont('', 10))
        treeView.setSortingEnabled(True)
        self.proxyModel.sort(0, QtCore.Qt.AscendingOrder)
        mainLayout.addWidget(treeView)

        treeView.clicked.connect(partial(self.selectItem))
        self.nameLineEdit.textChanged.connect(partial(self.lineEditModified))
        self.typeLineEdit.textChanged.connect(partial(self.lineEditModified))

        width = treeView.frameGeometry().width()
        height = treeView.frameGeometry().height()
        mainWindow.resize(450, 600)
        mainWindow.show()

    def selectItem(self, index, *args):
        sourceModel = self.proxyModel.sourceModel()
        mappedIndex = self.proxyModel.mapToSource(index)
        obj = sourceModel.itemFromIndex(mappedIndex)

        if obj is not None and cmds.objExists(obj):
            cmds.select(obj, replace=True)
            return
        cmds.select(clear=1)

    def lineEditModified(self, *args):
        if self.nameLineEdit.isModified():
            lineEdit = self.nameLineEdit
            filterKeyColumn = 0
        else:
            lineEdit = self.typeLineEdit
            filterKeyColumn = 1

        text = lineEdit.text()
        self.proxyModel.setFilterFixedString(text)
        self.proxyModel.setFilterKeyColumn(filterKeyColumn)
        self.nameLineEdit.setModified(False)
