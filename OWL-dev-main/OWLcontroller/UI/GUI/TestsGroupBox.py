from collections import namedtuple
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic, QtCore


class TestsGroupBox(QtWidgets.QGroupBox):
    def __init__(self, centralwidget,mainWindowRef,groupName,tests):
        super(TestsGroupBox, self).__init__(centralwidget)

        self.controller = mainWindowRef.controller
        self.setObjectName("hostExercisersGroupBox")
        self.vbox = QVBoxLayout()
        self.groupName = groupName
        self.tests = tests
        self.myHostPc = self.controller.configs.defaultConfContent['hostPCs'][0]

        self.testTableSetup()
        self.scrollSetup()
        self.checkAllSetup()

    def checkAllSetup(self):
        self.checkAllBox = QtWidgets.QCheckBox(self)
        self.checkAllBox.setGeometry(QtCore.QRect(1, 13, 200, 21))
        self.checkAllBox.setObjectName("checkAllBox")
        self.checkAllBox.clicked.connect(self.onCheckAllClicked)

    def testTableSetup(self):

        self.testsRows = {}
        for test in self.tests:

            groupBox = QtWidgets.QGroupBox()
            groupBox.setObjectName("GroupBox_"+test.testname)

            checkBox = QtWidgets.QCheckBox(groupBox)
            checkBox.setGeometry(QtCore.QRect(0, 1, 200, 21))
            checkBox.setObjectName("testCheckBox_"+test.testname)
            checkBox.clicked.connect(self.onCheckBoxClicked)


            repeatTestBox = QtWidgets.QSpinBox(groupBox)
            repeatTestBox.setGeometry(QtCore.QRect(200, 0, 47, 23))
            repeatTestBox.setObjectName("repeatTestBox_"+test.testname)
            repeatTestBox.setRange(0,1000)
            repeatTestBox.valueChanged.connect(self.repeatTestBoxChanged)

            statusLbl = QtWidgets.QLabel(groupBox)
            statusLbl.setGeometry(QtCore.QRect(270, 3, 100, 14))
            statusLbl.setObjectName("TestState_"+test.testname)

            groupBox.setFixedHeight(25)
            groupBox.setFixedWidth(500)

            self.vbox.addWidget(groupBox)

            TestRowNamedtuple = namedtuple('TestRow', ['checkBox', 'repeatTestBox','statusLbl'])
            self.testsRows[test.testname] = TestRowNamedtuple(checkBox, repeatTestBox, statusLbl)

    def repeatTestBoxChanged(self):
        repeatTestBox = self.sender()
        testName = repeatTestBox.objectName().split('_')[1]
        if testName in self.myHostPc['tests'].keys():
            self.myHostPc['tests'][testName]['repeatAmount'] = repeatTestBox.value()
        else:
            self.myHostPc['tests'][testName] = {"repeatAmount" : repeatTestBox.value(), "checked" : False}


    def onCheckBoxClicked(self):
        clickedCheckBox = self.sender()
        testName = clickedCheckBox.objectName().split('_')[1]
        if testName in self.myHostPc['tests'].keys():
            self.myHostPc['tests'][testName]['checked'] = clickedCheckBox.isChecked()
        else:
            self.myHostPc['tests'][testName] = {"repeatAmount" : 0, "checked" : clickedCheckBox.isChecked()}


    def scrollSetup(self):
        self.widget = QWidget()
        self.widget.setLayout(self.vbox)
        self.scroll = QScrollArea(self)  # Scroll Area which contains the widgets, set as the centralWidget
        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.scroll.setGeometry(QtCore.QRect(0, 30, 540, 250))


    def retranslateUi(self):
        self.setToolTip("tests list")
        self.setTitle(self.groupName + " tests")
        self.checkAllBox.setText("Check all")
        for test in self.tests:
            self.testsRows[test.testname].checkBox.setText(test.testname)
            self.testsRows[test.testname].statusLbl.setText("Not Started")

    def updateTestStatusLbl(self,testName,testStatus):
        _translate = QtCore.QCoreApplication.translate
        self.testsRows[testName].statusLbl.setText(_translate("skippedTestsNumber", testStatus))

    def loadHostPCSTestParams(self, hostPc):
        self.myHostPc = hostPc
        self.setTitle(self.groupName + " tests,   for " + self.myHostPc['IP'])
        for test in self.tests:
            if test.testname in self.myHostPc['tests']:
                savedTestParmsPerHostPc = self.myHostPc['tests'][test.testname]
                self.testsRows[test.testname].checkBox.setChecked(savedTestParmsPerHostPc['checked'])
                self.testsRows[test.testname].repeatTestBox.setValue(savedTestParmsPerHostPc['repeatAmount'])
            else:
                self.testsRows[test.testname].checkBox.setChecked(False)
                self.testsRows[test.testname].repeatTestBox.setValue(0)

            if self.myHostPc["IP"] in self.controller.runtimeHostPcsData.keys() \
                    and test.testname in self.controller.runtimeHostPcsData[self.myHostPc["IP"]].keys():
                self.testsRows[test.testname].statusLbl.setText(self.controller.runtimeHostPcsData[self.myHostPc["IP"]][test.testname])
            else:
                self.testsRows[test.testname].statusLbl.setText("Not Started")

    def onCheckAllClicked(self):
        for testRow in self.testsRows.values():
            testRow.checkBox.setChecked(self.checkAllBox.isChecked())
        for test in self.tests:
            if test.testname in self.myHostPc['tests'].keys():
                self.myHostPc['tests'][test.testname]['checked'] = self.checkAllBox.isChecked()
            else:
                self.myHostPc['tests'][test.testname] = {"repeatAmount": 0, "checked": self.checkAllBox.isChecked()}

    def clearAll(self):
        self.setTitle(self.groupName + " tests")
        for testRow in self.testsRows.values():
            testRow.checkBox.setChecked(False)
            testRow.repeatTestBox.setValue(0)
