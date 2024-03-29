# -*- coding: utf-8 -*-
'''
TITLE: Nastran Composite Processing Tool (NASCOMP)

Description:
Implementation of a processing script for NASTRAN composite output with simple GUI.
It contains data manipulation for Lamina Stress/Strain and Ply Strength Ratio
'''


from PyQt5 import QtCore, QtGui, QtWidgets
import patran_input
import sqlite3

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        '''
        Main Window details
        '''
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(818, 688)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 10, 781, 631))
        self.widget.setObjectName("widget")
        self.materialWidget = QtWidgets.QTabWidget(self.widget)
        self.materialWidget.setGeometry(QtCore.QRect(20, 160, 731, 411))
        self.materialWidget.setObjectName("materialWidget")
        '''
        Table of Elements grouping
        '''
        self.tab_group_elem = QtWidgets.QWidget()
        self.tab_group_elem.setObjectName("tab_group_elem")
        self.table_group_elem = QtWidgets.QTableWidget(self.tab_group_elem)
        self.table_group_elem.setGeometry(QtCore.QRect(320, 10, 391, 371))
        self.table_group_elem.setHorizontalHeaderLabels(['Group Name', 'Group Elements'])
        self.table_group_elem.setObjectName("table_group_elem")
        self.line_insert_group = QtWidgets.QLineEdit(self.tab_group_elem)
        self.line_insert_group.setGeometry(QtCore.QRect(10, 60, 281, 31))
        self.line_insert_group.setObjectName("line_insert_group")
        self.label_groups = QtWidgets.QLabel(self.tab_group_elem)
        self.label_groups.setGeometry(QtCore.QRect(10, 30, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_groups.setFont(font)
        self.label_groups.setObjectName("label_groups")
        self.label_elements = QtWidgets.QLabel(self.tab_group_elem)
        self.label_elements.setGeometry(QtCore.QRect(10, 110, 161, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_elements.setFont(font)
        self.label_elements.setObjectName("label_elements")
        self.line_insert_elments = QtWidgets.QLineEdit(self.tab_group_elem)
        self.line_insert_elments.setGeometry(QtCore.QRect(10, 140, 281, 31))
        self.line_insert_elments.setObjectName("line_insert_elments")
        #Push button to add group element with name and elements
        self.add_group_elem = QtWidgets.QPushButton(self.tab_group_elem)
        self.add_group_elem.clicked.connect(self.addGroup)
        self.add_group_elem.setGeometry(QtCore.QRect(20, 190, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.add_group_elem.setFont(font)
        self.add_group_elem.setObjectName("add_group_elem")
        #Push button to delete groups and elements
        self.del_group_elem = QtWidgets.QPushButton(self.tab_group_elem)
        self.del_group_elem.clicked.connect(self.delGroup)
        self.del_group_elem.setGeometry(QtCore.QRect(110, 190, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.del_group_elem.setFont(font)
        self.del_group_elem.setObjectName("del_group_elem")
        '''
        Material Tab
        '''
        self.materialWidget.addTab(self.tab_group_elem, "")
        self.tab_materials = QtWidgets.QWidget()
        self.tab_materials.setObjectName("tab_materials")
        #Label Mat Facing
        self.label_matFacing = QtWidgets.QLabel(self.tab_materials)
        self.label_matFacing.setGeometry(QtCore.QRect(20, 10, 161, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_matFacing.setFont(font)
        self.label_matFacing.setObjectName("label_matFacing")
        #Label Mat Core
        self.label_matCore_2 = QtWidgets.QLabel(self.tab_materials)
        self.label_matCore_2.setGeometry(QtCore.QRect(20, 120, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_matCore_2.setFont(font)
        self.label_matCore_2.setObjectName("label_matCore_2")
        ##Table Widget Materials facing
        self.tableView_facing = QtWidgets.QTableWidget(self.tab_materials)
        self.tableView_facing.setGeometry(QtCore.QRect(380, 40, 321, 81))
        self.tableView_facing.setObjectName("tableView_facing")

        ##Table Widget Materials Core
        self.tableView_core = QtWidgets.QTableWidget(self.tab_materials)
        self.tableView_core.setGeometry(QtCore.QRect(300, 150, 401, 181))
        self.tableView_core.setObjectName("tableView_core")

        #Text insert for material facing Name
        self.line_insert_mat_facing = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_mat_facing.setGeometry(QtCore.QRect(170, 40, 111, 31))
        self.line_insert_mat_facing.setObjectName("line_insert_mat_facing")
        #Text insert for material facing FOSU
        self.line_insert_facing_fosu = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_facing_fosu.setGeometry(QtCore.QRect(170, 80, 111, 31))
        self.line_insert_facing_fosu.setObjectName("line_insert_facing_fosu")

        self.label_matFacing_2 = QtWidgets.QLabel(self.tab_materials)
        self.label_matFacing_2.setGeometry(QtCore.QRect(20, 40, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_matFacing_2.setFont(font)
        self.label_matFacing_2.setObjectName("label_matFacing_2")
        self.label_facing_FOSu = QtWidgets.QLabel(self.tab_materials)
        self.label_facing_FOSu.setGeometry(QtCore.QRect(110, 80, 41, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_facing_FOSu.setFont(font)
        self.label_facing_FOSu.setObjectName("label_facing_FOSu")
        ###Push Button to add mat Facing and FOSU
        self.pushButton_add_facing = QtWidgets.QPushButton(self.tab_materials)
        self.pushButton_add_facing.setGeometry(QtCore.QRect(300, 80, 61, 31))
        self.pushButton_add_facing.setObjectName("pushButton_add_facing")
        self.pushButton_add_facing.clicked.connect(self.addMatFacing)

        ### Push button to del mat Facing and FOSU
        self.pushButton_delete_facing = QtWidgets.QPushButton(self.tab_materials)
        self.pushButton_delete_facing.setGeometry(QtCore.QRect(300, 40, 61, 31))
        self.pushButton_delete_facing.setObjectName("pushButton_delete_facing")
        self.pushButton_delete_facing.clicked.connect(self.delFacing)
        
        self.label_matCore = QtWidgets.QLabel(self.tab_materials)
        self.label_matCore.setGeometry(QtCore.QRect(20, 150, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_matCore.setFont(font)
        self.label_matCore.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_matCore.setObjectName("label_matCore")
        self.line_insert_core_id = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_core_id.setGeometry(QtCore.QRect(170, 150, 111, 31))
        self.line_insert_core_id.setObjectName("line_insert_core_id")
        self.label_FSL = QtWidgets.QLabel(self.tab_materials)
        self.label_FSL.setGeometry(QtCore.QRect(20, 190, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_FSL.setFont(font)
        self.label_FSL.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_FSL.setObjectName("label_FSL")
        self.line_insert_fsl = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_fsl.setGeometry(QtCore.QRect(170, 190, 111, 31))
        self.line_insert_fsl.setObjectName("line_insert_fsl")
        self.line_insert_fsw = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_fsw.setGeometry(QtCore.QRect(170, 230, 111, 31))
        self.line_insert_fsw.setObjectName("line_insert_fsw")
        self.label_FSW = QtWidgets.QLabel(self.tab_materials)
        self.label_FSW.setGeometry(QtCore.QRect(120, 230, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_FSW.setFont(font)
        self.label_FSW.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_FSW.setObjectName("label_FSW")
        self.label_FOSU = QtWidgets.QLabel(self.tab_materials)
        self.label_FOSU.setGeometry(QtCore.QRect(110, 270, 41, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_FOSU.setFont(font)
        self.label_FOSU.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_FOSU.setObjectName("label_FOSU")
        self.line_insert_core_fosu = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_core_fosu.setGeometry(QtCore.QRect(170, 270, 111, 31))
        self.line_insert_core_fosu.setObjectName("line_insert_core_fosu")
        self.line_insert_kdf = QtWidgets.QLineEdit(self.tab_materials)
        self.line_insert_kdf.setGeometry(QtCore.QRect(170, 310, 111, 31))
        self.line_insert_kdf.setObjectName("line_insert_kdf")
        self.label_KDF = QtWidgets.QLabel(self.tab_materials)
        self.label_KDF.setGeometry(QtCore.QRect(120, 310, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_KDF.setFont(font)
        self.label_KDF.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_KDF.setObjectName("label_KDF")
        #Push button to add core
        self.pushButton_add_core = QtWidgets.QPushButton(self.tab_materials)
        self.pushButton_add_core.setGeometry(QtCore.QRect(300, 340, 61, 31))
        self.pushButton_add_core.setObjectName("pushButton_add_core")
        self.pushButton_add_core.clicked.connect(self.addMatCore)
        #Push button to delete core
        self.pushButton_delete_core = QtWidgets.QPushButton(self.tab_materials)
        self.pushButton_delete_core.setGeometry(QtCore.QRect(370, 340, 61, 31))
        self.pushButton_delete_core.setObjectName("pushButton_delete_core")
        self.pushButton_delete_core.clicked.connect(self.delCore)
        
        self.line = QtWidgets.QFrame(self.tab_materials)
        self.line.setGeometry(QtCore.QRect(20, 130, 681, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_insert_core_kdf = QtWidgets.QFrame(self.tab_materials)
        self.line_insert_core_kdf.setGeometry(QtCore.QRect(20, 20, 681, 20))
        self.line_insert_core_kdf.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_insert_core_kdf.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_insert_core_kdf.setObjectName("line_insert_core_kdf")
        self.materialWidget.addTab(self.tab_materials, "")
        self.tab_output = QtWidgets.QWidget()
        self.tab_output.setObjectName("tab_output")
        self.excel_results = QtWidgets.QCheckBox(self.tab_output)
        self.excel_results.setGeometry(QtCore.QRect(30, 20, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.excel_results.setFont(font)
        self.excel_results.setObjectName("excel_results")
        self.excel_summary = QtWidgets.QCheckBox(self.tab_output)
        self.excel_summary.setGeometry(QtCore.QRect(30, 60, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.excel_summary.setFont(font)
        self.excel_summary.setObjectName("excel_summary")
        self.excel_mos_data = QtWidgets.QCheckBox(self.tab_output)
        self.excel_mos_data.setGeometry(QtCore.QRect(30, 100, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.excel_mos_data.setFont(font)
        self.excel_mos_data.setObjectName("excel_mos_data")
        self.word_table_output = QtWidgets.QCheckBox(self.tab_output)
        self.word_table_output.setGeometry(QtCore.QRect(30, 140, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.word_table_output.setFont(font)
        self.word_table_output.setObjectName("word_table_output")
        self.materialWidget.addTab(self.tab_output, "")
        self.start_calculation = QtWidgets.QPushButton(self.widget)
        self.start_calculation.setGeometry(QtCore.QRect(20, 590, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.start_calculation.setFont(font)
        self.start_calculation.setObjectName("start_calculation")
        self.progressBar = QtWidgets.QProgressBar(self.widget)
        self.progressBar.setGeometry(QtCore.QRect(150, 590, 331, 31))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.output_log = QtWidgets.QTextBrowser(self.widget)
        self.output_log.setGeometry(QtCore.QRect(490, 590, 261, 31))
        self.output_log.setObjectName("output_log")

        """
        Butoane pentru browse bdf, f06 si pch
        """
        
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 731, 141))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.browse_bdf = QtWidgets.QPushButton(self.groupBox)
        self.browse_bdf.clicked.connect(self.browseBDF) #Buton browse BDF
        self.browse_bdf.setGeometry(QtCore.QRect(620, 20, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.browse_bdf.setFont(font)
        self.browse_bdf.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.browse_bdf.setObjectName("browse_bdf")
        self.browse_f06 = QtWidgets.QPushButton(self.groupBox)
        self.browse_f06.clicked.connect(self.browseF06) #Buton browse F06
        self.browse_f06.setGeometry(QtCore.QRect(620, 60, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.browse_f06.setFont(font)
        self.browse_f06.setObjectName("browse_f06")
        self.browse_pch = QtWidgets.QPushButton(self.groupBox)
        self.browse_pch.clicked.connect(self.browsePCH) #Buton browse PCH
        self.browse_pch.setGeometry(QtCore.QRect(620, 100, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.browse_pch.setFont(font)
        self.browse_pch.setObjectName("browse_pch")
        self.label_bdf = QtWidgets.QLabel(self.groupBox)
        self.label_bdf.setGeometry(QtCore.QRect(20, 20, 41, 31))
        self.label_bdf.setObjectName("label_bdf")
        self.label_f06 = QtWidgets.QLabel(self.groupBox)
        self.label_f06.setGeometry(QtCore.QRect(20, 60, 41, 31))
        self.label_f06.setObjectName("label_f06")
        self.label_pch = QtWidgets.QLabel(self.groupBox)
        self.label_pch.setGeometry(QtCore.QRect(20, 100, 41, 31))
        self.label_pch.setObjectName("label_pch")
        self.browse_view_f06 = QtWidgets.QTextBrowser(self.groupBox)
        self.browse_view_f06.setGeometry(QtCore.QRect(70, 60, 521, 31))
        self.browse_view_f06.setObjectName("browse_view_f06")
        self.browse_view_bdf = QtWidgets.QTextBrowser(self.groupBox)
        self.browse_view_bdf.setGeometry(QtCore.QRect(70, 20, 521, 31))
        self.browse_view_bdf.setObjectName("browse_view_bdf")
        self.browse_view_pch = QtWidgets.QTextBrowser(self.groupBox)
        self.browse_view_pch.setGeometry(QtCore.QRect(70, 100, 521, 31))
        self.browse_view_pch.setObjectName("browse_view_pch")

        """
        Central Widget Main Window
        """

        #########################
        #Menu Bar (File, About)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 818, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        #Create New Sub-Menu, clear database
        newButton = self.menuFile.addAction('New')
        newButton.setShortcut('Ctrl+N')
        
        #Create Exit Sub-menu for the FILE menubar
        exitButton = self.menuFile.addAction('Exit')
        exitButton.setShortcut('Ctrl+Q')
        # Check int=main, window=w, this is what needs to be closed
        exitButton.triggered.connect(w.close)


        # Help - About - message box when button triggered
        def about_popup():
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle('Info')
            msg.setText('This program is property of o\\')
            msg.setStandardButtons(msg.Ok)
            msg.exec_()
            
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        aboutButton = self.menuHelp.addAction('About')
        aboutButton.triggered.connect(lambda: about_popup())
            
        # Status Bar Definition, File and Help menus        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        
        #End Menu Definition
        #########################


        self.retranslateUi(MainWindow)
        self.materialWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.browse_bdf, self.browse_f06)
        MainWindow.setTabOrder(self.browse_f06, self.browse_pch)
        MainWindow.setTabOrder(self.browse_pch, self.browse_view_bdf)
        MainWindow.setTabOrder(self.browse_view_bdf, self.browse_view_f06)
        MainWindow.setTabOrder(self.browse_view_f06, self.browse_view_pch)
        MainWindow.setTabOrder(self.browse_view_pch, self.materialWidget)
        MainWindow.setTabOrder(self.materialWidget, self.excel_results)
        MainWindow.setTabOrder(self.excel_results, self.excel_summary)
        MainWindow.setTabOrder(self.excel_summary, self.excel_mos_data)
        MainWindow.setTabOrder(self.excel_mos_data, self.word_table_output)
        MainWindow.setTabOrder(self.word_table_output, self.start_calculation)
        MainWindow.setTabOrder(self.start_calculation, self.output_log)


    def addGroup(self):
        string_elements=self.line_insert_elments.text()
        string_group_name=self.line_insert_group.text()
        #Process data with Patran_input.py
        result_list_elm = patran_input.process_input(string_elements)
        self.table_group_elem.setHorizontalHeaderLabels(['Group Name','Elements'])
        numRows = self.table_group_elem.rowCount()
        self.table_group_elem.setColumnCount(2)
        self.table_group_elem.insertRow(numRows)
        self.table_group_elem.setItem(numRows, 0, QtWidgets.QTableWidgetItem(string_group_name))
        self.table_group_elem.setItem(numRows, 1, QtWidgets.QTableWidgetItem(str(result_list_elm)))

    def addMatFacing(self):
        #Check if input is float
        string_mat_facing = self.line_insert_mat_facing.text()
        string_facing_fosu=self.line_insert_facing_fosu.text()
        numRows = self.tableView_facing.rowCount()
        self.tableView_facing.setHorizontalHeaderLabels(['Material','FOSU'])
        self.tableView_facing.setColumnCount(2)
        self.tableView_facing.insertRow(numRows)
        self.tableView_facing.setItem(numRows, 0, QtWidgets.QTableWidgetItem(string_mat_facing))
        self.tableView_facing.setItem(numRows, 1, QtWidgets.QTableWidgetItem(string_facing_fosu))

    def addMatCore(self):
        string_mat_core = self.line_insert_core_id.text()
        string_core_fsl = self.line_insert_fsl.text()
        string_core_fsw = self.line_insert_fsw.text()
        string_core_fosu = self.line_insert_core_fosu.text()
        string_core_kdf = self.line_insert_kdf.text()
        self.tableView_core.setHorizontalHeaderLabels(['Material','FsL','FsW','FOSU','KDF'])
        numRows = self.tableView_core.rowCount()
        self.tableView_core.setColumnCount(4)
        self.tableView_core.insertRow(numRows)
        self.tableView_core.setItem(numRows, 0, QtWidgets.QTableWidgetItem(string_mat_core))
        self.tableView_core.setItem(numRows, 1, QtWidgets.QTableWidgetItem(string_core_fsl))
        self.tableView_core.setItem(numRows, 2, QtWidgets.QTableWidgetItem(string_core_fsw))
        self.tableView_core.setItem(numRows, 3, QtWidgets.QTableWidgetItem(string_core_fosu))
        self.tableView_core.setItem(numRows, 4, QtWidgets.QTableWidgetItem(string_core_kdf))

        
    def delCore(self):
        self.tableView_core.removeRow(self.tableView_core.currentRow())

    def delFacing(self):
        self.tableView_facing.removeRow(self.tableView_facing.currentRow())

    def delGroup(self):
        self.table_group_elem.removeRow(self.table_group_elem.currentRow())

        
    def browseBDF(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select BDF file", "", "BDF Files (*.bdf)")
        if fileName:
            self.browse_view_bdf.clear()
            self.browse_view_bdf.append(fileName)

    def browseF06(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select F06 file", "", "F06 Files (*.f06)")
        if fileName:
            self.browse_view_bdf.clear()
            self.browse_view_f06.append(fileName)

    def browsePCH(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select PCH file", "", "PCH Files (*.pch)")
        if fileName:
            self.browse_view_bdf.clear()
            self.browse_view_pch.append(fileName)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "INCOMP"))
        self.label_groups.setText(_translate("MainWindow", "Group Name"))
        self.label_elements.setText(_translate("MainWindow", "Elements in Group"))
        self.add_group_elem.setText(_translate("MainWindow", "Add"))
        self.del_group_elem.setText(_translate("MainWindow", "Delete"))
        self.materialWidget.setTabText(self.materialWidget.indexOf(self.tab_group_elem), _translate("MainWindow", "Groups Input"))
        self.label_matFacing.setText(_translate("MainWindow", "Material Facing"))
        self.label_matCore_2.setText(_translate("MainWindow", "Material Core"))
        self.label_matFacing_2.setText(_translate("MainWindow", "Material Facing Name/ID"))
        self.label_facing_FOSu.setText(_translate("MainWindow", "FOSu"))
        self.pushButton_add_facing.setText(_translate("MainWindow", "Add"))
        self.pushButton_delete_facing.setText(_translate("MainWindow", "Delete"))
        self.label_matCore.setText(_translate("MainWindow", "Material Core Name/ID"))
        self.label_FSL.setText(_translate("MainWindow", "FsL"))
        self.label_FSW.setText(_translate("MainWindow", "FsW"))
        self.label_FOSU.setText(_translate("MainWindow", "FOSu"))
        self.label_KDF.setText(_translate("MainWindow", "KDF"))
        self.pushButton_add_core.setText(_translate("MainWindow", "Add"))
        self.pushButton_delete_core.setText(_translate("MainWindow", "Delete"))
        self.materialWidget.setTabText(self.materialWidget.indexOf(self.tab_materials), _translate("MainWindow", "Materials Input"))
        self.excel_results.setText(_translate("MainWindow", "Excel Summary Data from F06 and PCH "))
        self.excel_summary.setText(_translate("MainWindow", "Excel Minimum MOS Summary  "))
        self.excel_mos_data.setText(_translate("MainWindow", "Excel MOS Data Calculation"))
        self.word_table_output.setText(_translate("MainWindow", "Word Table and Report Output"))
        self.materialWidget.setTabText(self.materialWidget.indexOf(self.tab_output), _translate("MainWindow", "Output Request"))
        self.start_calculation.setText(_translate("MainWindow", "START"))
        self.groupBox.setTitle(_translate("MainWindow", "Input Files"))
        self.browse_bdf.setText(_translate("MainWindow", "Browse"))
        self.browse_f06.setText(_translate("MainWindow", "Browse"))
        self.browse_pch.setText(_translate("MainWindow", "Browse"))
        self.label_bdf.setText(_translate("MainWindow", "BDF"))
        self.label_f06.setText(_translate("MainWindow", "F06"))
        self.label_pch.setText(_translate("MainWindow", "PCH"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))




if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    w = QtWidgets.QMainWindow()
    window.setupUi(w)
    w.show()
    sys.exit(app.exec_())
