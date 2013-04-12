# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EditCommandDialog.ui'
#
# Created: Thu Apr 11 21:40:39 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DialogEditCommandList(object):
    def setupUi(self, DialogEditCommandList):
        DialogEditCommandList.setObjectName(_fromUtf8("DialogEditCommandList"))
        DialogEditCommandList.resize(538, 350)
        DialogEditCommandList.setModal(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DialogEditCommandList)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_2 = QtGui.QGroupBox(DialogEditCommandList)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEditAdd = QtGui.QLineEdit(self.groupBox_2)
        self.lineEditAdd.setObjectName(_fromUtf8("lineEditAdd"))
        self.horizontalLayout.addWidget(self.lineEditAdd)
        self.pushButtonAdd = QtGui.QPushButton(self.groupBox_2)
        self.pushButtonAdd.setObjectName(_fromUtf8("pushButtonAdd"))
        self.horizontalLayout.addWidget(self.pushButtonAdd)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(DialogEditCommandList)
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.listWidgetCommand = QtGui.QListWidget(self.groupBox)
        self.listWidgetCommand.setDragEnabled(True)
        self.listWidgetCommand.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.listWidgetCommand.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listWidgetCommand.setAlternatingRowColors(True)
        self.listWidgetCommand.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidgetCommand.setObjectName(_fromUtf8("listWidgetCommand"))
        self.verticalLayout.addWidget(self.listWidgetCommand)
        self.pushButtonDelete = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonDelete.sizePolicy().hasHeightForWidth())
        self.pushButtonDelete.setSizePolicy(sizePolicy)
        self.pushButtonDelete.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButtonDelete.setObjectName(_fromUtf8("pushButtonDelete"))
        self.verticalLayout.addWidget(self.pushButtonDelete)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(DialogEditCommandList)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(DialogEditCommandList)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DialogEditCommandList.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DialogEditCommandList.reject)
        QtCore.QObject.connect(self.lineEditAdd, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.pushButtonAdd.click)
        QtCore.QMetaObject.connectSlotsByName(DialogEditCommandList)
        DialogEditCommandList.setTabOrder(self.lineEditAdd, self.pushButtonAdd)
        DialogEditCommandList.setTabOrder(self.pushButtonAdd, self.pushButtonDelete)
        DialogEditCommandList.setTabOrder(self.pushButtonDelete, self.buttonBox)

    def retranslateUi(self, DialogEditCommandList):
        DialogEditCommandList.setWindowTitle(QtGui.QApplication.translate("DialogEditCommandList", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("DialogEditCommandList", "Agregar comando", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonAdd.setText(QtGui.QApplication.translate("DialogEditCommandList", "Agregar a la lista", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("DialogEditCommandList", "Editar lista", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonDelete.setText(QtGui.QApplication.translate("DialogEditCommandList", "Borrar seleccionados", None, QtGui.QApplication.UnicodeUTF8))

