import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication,QMainWindow, QAction,QSplitter,QGraphicsDropShadowEffect
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import Qt,QSize,QMargins
#import first.py
import pymysql
from gui2 import Form2
from sign_up import Sign_Up
from new import Example

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class Authorization(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        screenShape = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(int(screenShape.width()/2)-375, int(screenShape.height()/2)-250, 750, 500)
        self.setFixedSize(750,500)
        self.setWindowTitle("Authorization")

        extractAction = QAction(QtGui.QIcon('door_exit.png'), 'Exit', self)
        extractAction.triggered.connect(self.close_app)
        #self.toolbar = self.addToolBar('Exit')
        #self.toolbar.addAction(extractAction)

        self.auto = QtWidgets.QLabel("Autorization")
        self.auto.setFixedSize(410,20)
        self.auto.setObjectName('auto')
        self.id = QtWidgets.QLabel("Your login ")
        self.password = QtWidgets.QLabel("Your password  ")
        self.idEdit = QtWidgets.QLineEdit()
        self.passEdit = QtWidgets.QLineEdit()
        self.passEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.signInBtn = QtWidgets.QPushButton("Sign in")
        self.signUpBtn = QtWidgets.QPushButton("Sign up")
        self.signInBtn.clicked.connect(lambda: self.btn_click(self.signInBtn))
        self.signUpBtn.clicked.connect(lambda: self.btn_click(self.signUpBtn))
        self.signUpBtn.setMaximumWidth(120)
        self.signInBtn.setMaximumWidth(120)

        im1 = QtWidgets.QLabel()
        im1.setFixedSize(60,60)
        im1.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/1(1).png")))
        im1.setScaledContents(True)

        im2 = QtWidgets.QLabel()
        im2.setFixedSize(60, 60)
        im2.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/2(1).png")))
        im2.setScaledContents(True)

        im3 = QtWidgets.QLabel()
        im3.setFixedSize(60, 56)
        im3.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/3(1).png")))
        im3.setScaledContents(True)

        im4 = QtWidgets.QLabel()
        im4.setFixedSize(50, 55)
        im4.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/4(1).png")))
        im4.setScaledContents(True)

        im5 = QtWidgets.QLabel()
        im5.setFixedSize(65, 65)
        im5.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/5(1).png")))
        im5.setScaledContents(True)

        im6 = QtWidgets.QLabel()
        im6.setFixedSize(60, 60)
        im6.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/6(1).png")))
        im6.setScaledContents(True)

        im7 = QtWidgets.QLabel()
        im7.setFixedSize(50, 48)
        im7.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/7(1).png")))
        im7.setScaledContents(True)

        im8 = QtWidgets.QLabel()
        im8.setFixedSize(54, 49)
        im8.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/8(1).png")))
        im8.setScaledContents(True)

        im9 = QtWidgets.QLabel()
        im9.setFixedSize(61, 61)
        im9.setPixmap(QtGui.QPixmap(QtGui.QImage("images/icons/9(1).png")))
        im9.setScaledContents(True)

        self.form_widget=QWidget()
        self.form_widget.setObjectName('form')
        self.form_widget.setFixedSize(410,130)

        self.grid = QtWidgets.QGridLayout(self.form_widget)
        self.grid.setContentsMargins(15, 15, 15, 15)
        self.grid.setSpacing(10)
        self.grid.addWidget(self.id, 0, 0)
        self.grid.addWidget(self.idEdit, 0, 1)
        self.grid.addWidget(self.password, 1, 0)
        self.grid.addWidget(self.passEdit, 1, 1)

        self.auto.setFixedHeight(30)
        self.auto.setAlignment(Qt.AlignCenter)
        self.grid.setAlignment(Qt.AlignCenter)
        self.idEdit.setMaximumWidth(200)
        self.idEdit.setMinimumWidth(70)
        self.passEdit.setMaximumWidth(200)
        self.passEdit.setMinimumWidth(70)
        self.id.setFixedSize(120, 20)
        self.password.setFixedSize(120, 20)

        self.btn_widget=QWidget()
        self.btn_widget.setFixedSize(300,70)
        self.btn_layout = QtWidgets.QHBoxLayout(self.btn_widget)
        self.btn_layout.addWidget(self.signInBtn)
        self.btn_layout.addWidget(self.signUpBtn)

        self.main_widget = QWidget()

        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.main_layout.addWidget(im1,0,0)
        self.main_layout.addWidget(im2,1,3)
        self.main_layout.addWidget(im3,0,7)
        self.main_layout.addWidget(im4,1,9)
        self.main_layout.addWidget(im5,3,1)
        self.main_layout.addWidget(im6,5,2)
        self.main_layout.addWidget(im7,4,7)
        self.main_layout.addWidget(im8,6,8)
        self.main_layout.addWidget(im9,6,0)

        #self.main_layout.addWidget(QtWidgets.QLabel(""), 0, 0, 1, 4)
        self.main_layout.addWidget(self.auto, 2, 3,1,4)
        self.main_layout.addWidget(self.form_widget, 3, 3, 1, 4)
        self.main_layout.addWidget(self.btn_widget, 5, 4,1,2)
        #self.main_layout.addWidget(QtWidgets.QLabel(""), 5, 0)

        self.check = QtWidgets.QCheckBox("Don't show images")
        self.main_layout.addWidget(self.check,6,3,1,4)
        self.check.stateChanged.connect(lambda:self.btnstate(self.check))
        self.selected=False

        self.setCentralWidget(self.main_widget)

        self.setStyleSheet("""
                        QMainWindow { border-image: url(images/back2.jpg);}
                        QPushButton { border-radius: 4px;
                                      background: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, stop:0 rgba(69,81,104,0.5), stop:1 rgba(2,19,25,0.95));
                                      height:30px;
                                      border: 1px solid rgba(0,0,0, 0.3);}
                        QWidget {font: 18px; color:white;}
                        #auto,#form {background-color:rgba(0,0,0,0.65);}
                        QLineEdit {border-radius: 2px;
                                    background-color:rgba(0,0,0,0.15);
                                    border: 1px solid rgba(0,0,0, 0.3);}
        """)

        #self.setStyleSheet("""
        #                QMainWindow { border-image: url(images/back5.jpg);}
        #                QPushButton { border-radius: 4px;
        #                              background: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, stop:0 rgba(69,81,104,0.5), stop:1 rgba(2,19,25,0.95));
        #                              height:30px;
        #                              border: 1px solid rgba(0,0,0, 0.3);}
        #                QWidget {font: 18px; color:white;}
        #                QLineEdit {border-radius: 2px;
        #                            background-color:rgba(0,0,0,0.15);
        #                            border: 1px solid rgba(255,255,255, 0.3);}
        #                #auto,#form {background-color:rgba(0,0,0,0.65);}
        #                """)
        self.show()

    def btn_click(self,b):
        if b.text()=='Sign in':
            if hasattr(self, 'message'):
                self.main_layout.removeWidget(self.message)
                self.message.deleteLater()
                del self.message
            id=self.idEdit.text()
            pswd=self.passEdit.text()

            connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
            cursor = connection.cursor()
            sql="SELECT * FROM `users` WHERE `Name`=%s"
            cursor.execute(sql, (id,))
            line=cursor.fetchone()
            if line is None:
                    self.message = QtWidgets.QLabel("Incorrect login.")
                    self.main_layout.addWidget(self.message,4,3,1,4)
            else:
                    if pswd==line[2]:
                        self.message = QtWidgets.QLabel("Success")
                        self.main_layout.addWidget(self.message,4,3,1,4)
                        self.dialog = Form2(line[0],self.selected)
                        self.dialog.show()
                        self.close()
                    else:
                        self.message = QtWidgets.QLabel("Incorrect password.")
                        self.main_layout.addWidget(self.message,4,3,1,4)
            #self.message.setAlignment(Qt.AlignCenter)
            self.message.setFixedSize(200,20)
            self.message.setObjectName('message')
            self.message.setStyleSheet('QLabel#message {color: rgba(255,0,0,0.7); font:17px;}')

        if b.text()=='Sign up':
            self.dialog = Sign_Up(self.selected)
            self.dialog.show()
            self.close()

    def btnstate(self,b):
        if b.isChecked() == True:
            self.selected=True
        else:
            self.selected=False

    def close_app(self):
        sys.exit()

app = QApplication(sys.argv)
ex = Authorization()
sys.exit(app.exec_())

