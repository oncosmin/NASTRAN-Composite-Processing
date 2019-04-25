"""
Test Browser button function
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class MyWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("Main Window")
        MainWindow.resize(500, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralWidget")
        self.centralwidget.setGeometry(0,0,500,400)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 40, 40))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("Start")
        self.textBrowser= QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0,50,161,100))
        self.textBrowser.setObjectName("listWidget")
        

        self.pushButton.clicked.connect(self.printMessage)

        self.add_group_elem = QtWidgets.QPushButton(self.centralwidget)
        self.add_group_elem.setGeometry(QtCore.QRect(0, 160, 75, 31))
        self.add_group_elem.clicked.connect(self.addGroupElements)

        self.del_group_elem = QtWidgets.QPushButton(self.centralwidget)
        self.del_group_elem.setGeometry(QtCore.QRect(100, 160, 75, 31))
        #self.del_group_elem.clicked.connect(self.delGroupElements)
        
        self.add_group_elem.setText( "Add")
        self.del_group_elem.setText( "Delete")

        self.line_insert_group = QtWidgets.QLineEdit(self.centralwidget)
        self.line_insert_group.setGeometry(QtCore.QRect(0, 200, 281, 31))
        self.line_insert_group.setObjectName("line_insert_group")
        
        self.table_group_elem = QtWidgets.QTableWidget(self.centralwidget)
        self.table_group_elem.setGeometry(QtCore.QRect(0, 250, 400, 100))
        self.table_group_elem.setObjectName("table_group_elem")
        self.table_group_elem.setColumnCount(2)


    def addGroupElements(self):
        value=str(self.line_insert_group.text())
        self.line_insert_group.clear()
        numRows = self.table_group_elem.rowCount()
        print (numRows)
        self.table_group_elem.insertRow(numRows+1)
        self.table_group_elem.setItem(numRows,1,value)


    #def delGroupElements(self):



    def printMessage(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select BDF file", "", "BDF Files (*.bdf)")
        if fileName:
            self.textBrowser.append(fileName)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    window = MyWindow()
    window.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
