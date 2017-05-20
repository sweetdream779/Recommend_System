#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QWidget,QFrame,QScrollArea,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QGridLayout,QMainWindow, QDesktopWidget,QPushButton)
from PyQt5.QtGui import QFont
from  functools import partial
import urllib.request
import numpy as np
import os
import sip
from gui2 import Form2
from ratingWidget import RatingWidget

def getRates(id,films):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    rates=[]
    for i in range(len(films)):
        filmId=films[i][4]
        sql="SELECT `Rating` FROM `ratings` WHERE `UserID`=%s AND `MovieID`=%s"
        cursor.execute(sql,(id,filmId))
        if cursor.rowcount==0:
            rates.append(0)
        else:
            rate = cursor.fetchone()[0]
            rates.append(rate)
    return rates

def NumberEstemated(UserID):
    connection = pymysql.connect(host="localhost", user="root",
                                 passwd="", db="movies")
    cursor = connection.cursor()

    sql = "SELECT `MovieID` FROM `ratings` WHERE `UserID`=%s"
    cursor.execute(sql, (int(UserID),))
    numberEstimates = cursor.rowcount
    cursor.close()
    connection.close()
    return numberEstimates

def addUser():
    addColumn('Y.txt')
    addColumn('R.txt')

def getNewID():
    connection = pymysql.connect(host="localhost", user="root",
                                 passwd="", db="movies")
    cursor = connection.cursor()
    sql = "SELECT DISTINCT UserID FROM ratings"
    cursor.execute(sql)
    newID = cursor.rowcount+1
    addUser()
    cursor.close()
    connection.close()
    return newID

def addColumn(filename):
    f = open(filename, 'r')
    if filename=="Y.txt":
        o = open('output1.txt', 'w')
    else:
        o = open('output2.txt', 'w')
    for i, line in enumerate(f):
        l = line
        vals = l.split()
        vals.append(0)
        newLine = " ".join(str(x) for x in vals)+"\n"
        o.write(newLine)
    f.close()
    o.close()

def changeMatrix(numCol,numRow,newVal,filename):
    numCol=int(numCol)
    numRow=int(numRow)
    f = open(filename, 'r')
    for i, line in enumerate(f):
        if i == numRow - 1:
            l = line
            vals = l.split()
            vals[numCol - 1] = newVal
            newLine = " ".join(str(x) for x in vals)
            break
    f.close()
    o = open('output.txt', 'w')
    i = 0
    for line in open(filename):
        i = i + 1
        if i == numRow:
            line = newLine + "\n"
        o.write(line)
    o.close()
    os.remove(filename)
    os.rename("output.txt", filename)

def changeYmean(numCol,numRow,rate):
    numCol = int(numCol)
    numRow = int(numRow)
    f = open('R.txt', 'r')
    for i, line in enumerate(f):
        if i == numRow - 1:
            R=line.split()
            R[numCol - 1] = 1
            break
    f.close()
    f = open('Y.txt', 'r')
    for i, line in enumerate(f):
        if i == numRow - 1:
            Y = line.split()
            Y[numCol - 1] = rate
            break
    f.close()
    R=[int(s) for s in R]
    Y=[int(s) for s in Y]
    arrayR=np.array(R)
    arrayY=np.array(Y)
    idx = np.where(arrayR == 1)
    YmeanNew=np.mean(arrayY[idx])
    changeMatrix(1,numRow,YmeanNew,'Ymean.txt')

def insertRate(idUser, idMovie, rate,name,pswd):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    if os.path.exists('output1.txt'):
        os.remove('Y.txt')
        os.rename("output1.txt", 'Y.txt')
        os.remove('R.txt')
        os.rename("output2.txt", 'R.txt')
        sql = "INSERT INTO `users` (`UserID`,`Name`,`Password`) VALUES (%s,%s,%s)"
        cursor.execute(sql, (int(idUser),name,pswd))
        connection.commit()

    sql="SELECT `links`.`Id` FROM `links` WHERE `links`.`MovieID`=%s"
    cursor.execute(sql,(int(idMovie),))
    idLink = cursor.fetchone()[0]
    cursor.close()
    row=idLink
    col=idUser
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    sql1 = "SELECT * FROM `ratings` WHERE `UserID`=%s AND `MovieID`=%s"
    cursor.execute(sql1, (int(idUser), int(idMovie)))
    if cursor.rowcount == 0:
        sql = "INSERT INTO `ratings` (`UserID`, `MovieID`,`Rating`) VALUES (%s, %s, %s)"
        cursor1.execute(sql, (int(idUser), int(idMovie), int(rate)))
    else:
        sql = "UPDATE `ratings` SET `Rating`=%s WHERE `UserID`=%s AND `MovieID`=%s"
        cursor1.execute(sql, (int(rate), int(idUser), int(idMovie)))
    changeMatrix(col,row,rate,'Y.txt')
    changeMatrix(col,row,1,'R.txt')
    changeYmean(col,row,rate)
    connection.commit()
    cursor.close()
    cursor1.close()
    connection.close()

class Example(QMainWindow):
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!self.UserID = id
    def __init__(self,name,pswd,selected):
        super().__init__() #Метод super() возвращает объект родителя класса Example и мы вызываем его конструктор
        self.Name=name
        self.Password=pswd
        self.selected=selected
        self.initUI()#initUI() отвечает за создание GUI

    def initUI(self):
        self.UserID = getNewID()
        self.screenShape = QDesktopWidget().screenGeometry()
        self.resize(self.screenShape.width() - 10, self.screenShape.height() - 100)
        self.setMinimumWidth(1300)

        self.btn_next_widget = QWidget()
        self.nextButton = QPushButton("Next")
        self.nextButton.setObjectName('Next_btn')
        self.btn_h_layout = QHBoxLayout()
        self.btn_h_layout.addStretch(1)
        self.btn_h_layout.addWidget(self.nextButton)
        self.btn_v_layout = QVBoxLayout(self.btn_next_widget)
        self.btn_v_layout.addStretch(1)
        self.btn_v_layout.addLayout(self.btn_h_layout)
        self.setLayout(self.btn_v_layout)

        self.LabelID = QLabel("Your login: "+self.Name)
        self.LabelID.setFixedSize(300,30)
        self.LabelID.setObjectName("l")

        self.Label1 = QLabel("Number of films you have estemated: ")
        self.Label2 = QLabel("0")
        self.LabelWidget=QWidget()
        self.LabelLayout = QHBoxLayout(self.LabelWidget)
        self.LabelLayout.addWidget(self.Label1)
        self.LabelLayout.addWidget(self.Label2)
        self.LabelWidget.setFixedSize(300,40)
        self.Label1.setObjectName("Label1")
        self.Label2.setObjectName("Label2")

        self.please = QLabel("Please rate the movies you watched (min 10)")
        self.please.setObjectName('style-label')
        self.please.setFont(QFont('SansSerif', 12))
        self.searchEdit = QLineEdit()#!!!!!!!!!!!!!!!!!
        self.searchBtn = QPushButton("Search")
        self.searchBtn.setObjectName('Search_btn')
        self.searchBtn.setShortcut('enter')
        self.searchBtn.setFont(QFont('SansSerif', 12))
        self.searchBtn.resize(self.searchBtn.sizeHint())
        self.searchBtn.clicked.connect(lambda: self.btn_click(self.searchBtn))
        self.mainWindow = QWidget()  # куда будут загружаться фильмы
        self.mainWindow.setObjectName('mainWindow')
        self.filmsWindow = QGridLayout(self.mainWindow)
        self.filmsWindow.setSpacing(10)
        self.filmsWindow.setObjectName('filmsWindow')

        self.searchBtn.setMaximumWidth(120)

        # SCROL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        self.main_widget = QWidget()
        self.main_widget.setObjectName('main')
        self.grid = QGridLayout(self.main_widget)
        self.grid.setContentsMargins(15, 15, 15, 15)
        self.grid.setSpacing(10)
        self.grid.addWidget(self.please, 0, 0)
        self.grid.addWidget(self.LabelWidget, 1, 0)
        self.grid.addWidget(self.LabelID, 2, 0)
        self.grid.addWidget(self.searchEdit, 3, 0)
        self.grid.addWidget(self.searchBtn, 3, 1)
        self.grid.addWidget(self.mainWindow, 4, 0)
        self.setLayout(self.grid)

        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidget(self.main_widget)
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.setFrameShape(QFrame.NoFrame)

        self.please.setFixedHeight(35)
        self.searchEdit.setMaximumWidth(1500)
        self.searchEdit.setMinimumWidth(300)
        self.setWindowTitle('Creating a profile')
        self.setWindowIcon(QIcon('2.png'))
        self.setCentralWidget(self.scrollWidget)
        self.setStyleSheet("""
                                   QLabel{color:white;
                                    font:15px;}
                                   #inform{background-color:rgba(0,0,0,0.3);}
                                   #main, #main_window {background-image: url(images/back1.jpg);background-attachment: fixed;}
                                   QSplitter::handle{background-color: transparent;}
                                   #style-label{
                                   font:17px;
                                       width: 55px;
                                       height: 18px;
                                       color:white;
                                   }
                                   #Label1,#Label2,#l{
                                   color:white;
                                   font:15px;
                                   }
                                   #button{
                                       font:15px;
                                       width: 55px;
                                       height: 18px;
                                       color:white;
                                       background-color:rgba(5,232,217,0.3);
                                       border:1px solid rgba(0,0,0, 0.8);
                                   }
                                   #Search_btn, #Next_btn {
                                    font:15px;
                                       width: 55px;
                                       height: 18px;
                                       color:white;
                                       background-color:rgba(0,0,0,0.3);
                                       border:1px solid rgba(0,0,0, 0.8);}
                                   QLineEdit{border-radius: 2px;
                                           background-color:rgba(0,0,0,0.3);
                                           border: 1px solid rgba(255,255,255, 0.3);
                                           color:white;
                                           font:20px;
                                          }
                                          QSplitter::handle{background-color: transparent;}

                                    QScrollBar:vertical {
                                            border: 1px solid #999999;
                                            background:white;
                                            width:10px;
                                            margin: 15px 0px 15px 0px;
                                      }

                                      QScrollBar::handle:vertical {
                                                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop: 0  rgb(69,81,104),  stop:1 rgb(2,19,25));
                                              min-height: 10px;
                                      }

                                      QScrollBar::add-line:vertical {
                                        background: none;
                                                    height:15 px;
                                                   subcontrol-position: bottom;
                                                    subcontrol-origin: margin;
                                      }

                                      QScrollBar::sub-line:vertical {
                                                background: none;
                                                height: 15px;
                                                subcontrol-position: top;
                                                subcontrol-origin: margin;
                                      }

                                      QScrollBar::up-arrow:vertical {
                                        image:url('images/up.png');
                                        height: 15px;
                                        width: 15px
                                      }

                                      QScrollBar::down-arrow:vertical {
                                        image:url('images/down.png');
                                        height: 15px;
                                        width: 15px
                                      }
                                    """)

    def print_imgs(self,films):
        self.myRates = getRates(self.UserID, films)
        j = -2
        self.bool = []
        for i in range(len(films)):
            ost = i % 5
            if (ost == 0):
                j = j + 2
            w = QWidget()
            layout = QGridLayout(w)
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            title = QLabel(films[i][0] + " (" + str(films[i][1]) + ")")
            title.setObjectName('style-label')
            imdb = QLabel("Imdb: " + str(films[i][3]))
            ganres = QLabel(films[i][5].replace("|", ", "))
            ganres.setWordWrap(True)
            title.setWordWrap(True)
            imdb.setObjectName('style-label')
            im = QLabel()
            im.setObjectName('style-label')
            if(not self.selected):
                data = urllib.request.urlopen(films[i][2]).read()
                image = QImage()
                image.loadFromData(data)
                wid = image.width()
                hei = image.height()
                pixmap = QPixmap(image)
                pixmap = pixmap.scaled(wid, hei)
                im.setPixmap(pixmap)
                im.setFixedSize(wid, hei)
                self.width = pixmap.width()
            else:
                self.width=182

            yourRating = QWidget()
            yourRating_layout = QHBoxLayout(yourRating)
            rating_label = QLabel('Your rate:')
            rating_label.setObjectName('style-label')
            rating_value = QLabel(str(self.myRates[i]))
            rating_value.setObjectName('style-label')
            yourRating_layout.addWidget(rating_label)
            yourRating_layout.addWidget(rating_value)
            rates = QWidget()
            rates_layout = QHBoxLayout(rates)
            rates_layout.addWidget(imdb)
            rates_layout.setSpacing(5)
            button = QPushButton("Estimate")
            button.setObjectName('button')
            button.setFixedSize(75, 23)
            self.bool.append(False)
            button.clicked.connect(partial(self.get_inform, films[i][4], j, ost, i, rating_value))
            rates_layout.addWidget(button)

            inform = QWidget()
            imform_layout = QVBoxLayout(inform)
            layout.addWidget(im, 0, 0)
            imform_layout.addWidget(title)
            imform_layout.addWidget(ganres)
            imform_layout.addWidget(rates)
            imform_layout.addWidget(yourRating)
            layout.addWidget(inform, 1, 0)
            inform.setFixedWidth(self.width)
            inform.setObjectName("inform")
            self.filmsWindow.addWidget(w, j, ost)
            self.filmsWindow.setSpacing(20)
        self.setLayout(self.filmsWindow)

    def get_inform(self,movieID,row,col,j,rating_value):
        stars=QWidget()
        #print(b, j, self.bool)
        stars.setMinimumWidth(self.width)
        stars_layout=QHBoxLayout(stars)
        stars_layout.setSpacing(0)
        for i in range(5):
            im = QLabel()
            pixmap = QPixmap("rating2.png")
            im.setPixmap(pixmap)
            stars_layout.addWidget(im)
        rating_widget = RatingWidget(num_icons=5)
        rating_widget.value_updated.connect(
            lambda value: self.setRating(str(value), movieID, rating_value)
        )
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(rating_widget)
        rate_widget = QWidget()
        rate_widget.setMinimumWidth(self.width)
        rate_widget.setLayout(rate_layout)
        if self.bool[j]==False:
            self.filmsWindow.addWidget(stars,row+1,col)
            self.bool[j]=True
            self.filmsWindow.addWidget(rate_widget,row+1,col)


    def setRating(self,value,movieID,rating_value):
        rating_value.setText(str(value))
        insertRate(self.UserID,movieID,value,self.Name,self.Password)
        count=NumberEstemated(self.UserID)
        self.Label2.setText(str(count))
        if count==3:
            self.grid.addWidget(self.btn_next_widget, 5, 0, 1, 2)
            self.nextButton.clicked.connect(lambda: self.next_btn_click(self.nextButton))

    def next_btn_click(self,button):
        self.dialog = Form2(self.UserID,self.selected)
        self.dialog.show()
        self.close()

    def btn_click(self, b):
        if hasattr(self, 'message'):
            sip.delete(self.message)
        if hasattr(self, 'filmsWindow'):
            #Перерисовка
            self.grid.removeWidget(self.mainWindow)
            self.mainWindow.deleteLater()
            self.mainWindow.setParent(None)
            del self.mainWindow
            #Вновь создаём область для загрузки фильмов--------------------------------------------
            self.mainWindow = QWidget()  # куда будут загружаться фильмы
            self.mainWindow.setObjectName('mainWindow')
            self.filmsWindow = QGridLayout(self.mainWindow)
            self.filmsWindow.setSpacing(10)
            self.filmsWindow.setObjectName('filmsWindow')
            self.grid.addWidget(self.mainWindow, 4, 0)

        film = self.searchEdit.text()
        if film=="":
            self.message=QLabel("Print the field, please.")
            self.grid.addWidget(self.message, 6, 0,1,2)
            self.message.setAlignment(Qt.AlignCenter)
            self.message.setObjectName('message')
            self.message.setStyleSheet('QLabel#message {color: white; font:17px;}')
        else:
            connection = pymysql.connect(host="localhost", user="root",
                                   passwd="", db="movies")
            cursor = connection.cursor()
            sql = "SELECT `movies`.`Title`,`movies`.`Year`,`links`.`Image`,`links`.`ImbdRate`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                          "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` WHERE `Title` LIKE %s "
            cursor.execute(sql, (('%'+film+'%',)))
            films = cursor.fetchall()
            if cursor.rowcount==0:
                self.message = QLabel("No such film.")
                self.grid.addWidget(self.message, 6, 0, 1, 2)
                self.message.setAlignment(Qt.AlignCenter)
                self.message.setObjectName('message')
                self.message.setStyleSheet('QLabel#message {color: white; font:17px;}')
            else:
                self.message = QLabel(" ")
                self.grid.addWidget(self.message, 6, 0, 1, 2)
                movies = []
                #num = cursor.rowcount
                i = 0
                for row in films:
                    movies.append([])
                    # Title,Year,Image,ImdbRate
                    movies[i].append(row[0])
                    movies[i].append(row[1])
                    movies[i].append(row[2])
                    movies[i].append(row[3])
                    movies[i].append(row[4])
                    movies[i].append(row[5])
                    i = i + 1

                cursor.close()
                connection.close()

                self.print_imgs(movies)

# ------------------------------------------------------------------------------------------------------

        #btn = QPushButton('Найти', self)
        #btn.setToolTip('This is a <b>QPushButton</b> widget')#Мы создаём виджет кнопки и устанавливаем всплывающую подсказку для неё.

        #btn.resize(btn.sizeHint())
        #btn.move(50, 50)
        #Меняем размер у кнопки, перемещаем её в окно. Метод sizeHint() даёт рекомендуемый размер для кнопки.

