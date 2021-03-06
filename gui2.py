import sys, os
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication,QMainWindow, QAction,QSplitter,QGraphicsDropShadowEffect,QSizePolicy,QScrollArea,QFrame
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import Qt,QSize,QMargins
from  first import ContentBased
import pymysql
from PyQt5.QtGui import QImage, QPalette, QBrush, QColor
import urllib.request
from gui3 import AllFilms
from  functools import partial
from ratingWidget import RatingWidget
import math
import numpy as np
from scipy.optimize import fmin_cg, minimize,check_grad
from main import collaborative_filtering
import sip
from my_ratings import MyRatings, getRates
import random

def getRecomends(id):
    #contentBased = ContentBased()
    #ids=contentBased.getPredictions(int(id),10)
    A = collaborative_filtering(int(id), nBestProducts=20)
    ids = A.makeRecommendation()
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    films = []
    j=0
    for i in range(len(ids)):
        cursor = connection.cursor()
        #sql="SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres`" \
        #              "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` WHERE `links`.`Id`=%s"
        sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres`,`links`.`Id`" \
                  "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` WHERE `movies`.`MovieID`=%s"
        cursor.execute(sql,(int(ids[i]),))
        film=cursor.fetchone()
        films.append([])
        # Title,Year,Image,ImdbRate,ID,Ganres
        films[j].append(film[2])
        films[j].append(film[3])
        films[j].append(film[0])
        films[j].append(film[1])
        films[j].append(film[4])
        films[j].append(film[5])
        j=j+1
        cursor.close()
    #A = collaborative_filtering(int(id),nBestProducts=10)
    #ids2 = A.makeRecommendation()
    #for i in range(len(ids)):
    #    cursor = connection.cursor()
    #    sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres`,`links`.`Id`" \
    #      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` WHERE `movies`.`MovieID`=%s"
    #    cursor.execute(sql, (int(ids2[i]),))
    #    film = cursor.fetchone()
    #    if film[6] in ids:
    #        continue
    #    films.append([])
        # Title,Year,Image,ImdbRate,ID,Ganres
    #    films[j].append(film[2])
    #    films[j].append(film[3])
    #    films[j].append(film[0])
     #   films[j].append(film[1])
    #    films[j].append(film[4])
    #    films[j].append(film[5])
    #    j=j+1
    #    cursor.close()
    #print(films)
    connection.close()
    return films

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
    o = open('output.txt', 'w')  # open for append
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

def insertRate(idUser, idMovie, rate):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
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
        #print("not exist")
        sql = "INSERT INTO `ratings` (`UserID`, `MovieID`,`Rating`) VALUES (%s, %s, %s)"
        cursor1.execute(sql, (int(idUser), int(idMovie), int(rate)))
    else:
        #print("exist")
        sql = "UPDATE `ratings` SET `Rating`=%s WHERE `UserID`=%s AND `MovieID`=%s"
        cursor1.execute(sql, (int(rate), int(idUser), int(idMovie)))
    changeMatrix(col,row,rate,'Y.txt')
    changeMatrix(col,row,1,'R.txt')
    changeYmean(col,row,rate)
    connection.commit()
    cursor.close()
    cursor1.close()
    connection.close()

def getLogin(UserID):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    sql="SELECT `Name` FROM `users` WHERE `UserID`=%s"
    cursor.execute(sql, (int(UserID),))
    name = cursor.fetchone()[0]
    return name

class Films(QWidget):
    def __init__(self,id,selected):
        super().__init__()
        self.UserID=id
        self.selected1=selected
        self.initUI()

    def initUI(self):
        self.grid=QtWidgets.QGridLayout()
        films=getRecomends(self.UserID)
        self.print_imgs(films)
        self.setLayout(self.grid)
        self.grid.setSpacing(5)

    def print_imgs(self,films):
        j=-2
        self.bool=[]
        for i in range(len(films)):
            ost=i%5
            if (ost==0):
                j=j+2
            w = QWidget()
            layout = QtWidgets.QGridLayout(w)
            layout.setSpacing(0)
            layout.setContentsMargins(0,0,0,0)
            title = QtWidgets.QLabel(films[i][0] + " (" + str(films[i][1]) + ")")
            imdb = QtWidgets.QLabel("Imdb: " + str(films[i][3]))
            ganres = QtWidgets.QLabel(films[i][5].replace("|",", "))
            title.setWordWrap(True)
            ganres.setWordWrap(True)
            #shadow = QGraphicsDropShadowEffect(self)
            #shadow.setBlurRadius(5)
            im = QtWidgets.QLabel()
            if(not self.selected1):
                data = urllib.request.urlopen(films[i][2]).read()
                image = QtGui.QImage()
                image.loadFromData(data)
                wid=image.width()
                hei=image.height()
                pixmap = QtGui.QPixmap(image)
                pixmap=pixmap.scaled(wid,hei)
                im.setPixmap(pixmap)
                im.setFixedSize(wid,hei)
                #im.setGraphicsEffect(shadow)
                self.width = pixmap.width()
                # print(width)
            else:
                self.width =182
            yourRating = QWidget()
            yourRating_layout = QtWidgets.QHBoxLayout(yourRating)
            rating_label = QtWidgets.QLabel('Your rate:')
            rating_value = QtWidgets.QLabel('0')
            yourRating_layout.addWidget(rating_label)
            yourRating_layout.addWidget(rating_value)

            rates=QWidget()
            rates_layout=QtWidgets.QHBoxLayout(rates)
            rates_layout.addWidget(imdb)
            button=QtWidgets.QPushButton("Estimate")
            button.setFixedSize(70,20)
            button.setObjectName("button")
            button.setStyleSheet("background-color:rgba(5,232,217,0.3); color:black; font:15px;")
            self.bool.append(False)
            button.clicked.connect(partial(self.estimate,films[i][4],j,ost,i,rating_value))
            rates_layout.addWidget(button)

            inform=QWidget()
            imform_layout = QtWidgets.QVBoxLayout(inform)

            layout.addWidget(im,0,0)

            imform_layout.addWidget(title)
            imform_layout.addWidget(ganres)
            imform_layout.addWidget(rates)
            imform_layout.addWidget(yourRating)
            layout.addWidget(inform,1,0)
            inform.setFixedWidth(self.width)
            inform.setObjectName("inform")
            self.grid.addWidget(w, j, ost)
            self.setStyleSheet("""
                QLabel{color:white;
                        font:15px;}
                #inform{background-color:rgba(0,0,0,0.3);}
            """)

    def estimate(self,movieID,row,col,j,rating_value):
        stars=QWidget()
        #print(b, j, self.bool)
        stars.setMinimumWidth(self.width)
        stars_layout=QtWidgets.QHBoxLayout(stars)
        stars_layout.setSpacing(0)
        for i in range(5):
            im = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap("rating2.png")
            im.setPixmap(pixmap)
            stars_layout.addWidget(im)
        #rating_value_widget = QtWidgets.QLabel('0')
        rating_widget = RatingWidget(num_icons=5)
        rating_widget.value_updated.connect(
            #lambda value: rating_value.setText(str(value))
            lambda value:self.setRating(str(value),movieID,rating_value)
        )
        rate_layout = QtWidgets.QHBoxLayout()
        rate_layout.addWidget(rating_widget)
        rate_widget = QtWidgets.QWidget()
        rate_widget.setMinimumWidth(self.width)
        rate_widget.setLayout(rate_layout)
        if self.bool[j]==False:
            self.grid.addWidget(stars,row+1,col)
            self.bool[j]=True
            #layout.addWidget(rating_value_widget,3,0)
            self.grid.addWidget(rate_widget,row+1,col)

    def setRating(self,value,movieID,rating_value):
        rating_value.setText(str(value))
        insertRate(self.UserID,movieID,value)

class Form2(QMainWindow):
    def __init__(self,id,selected):
        super().__init__()
        self.UserID=id
        self.selected=selected
        self.initUI()

    def initUI(self):
        self.screenShape = QtWidgets.QDesktopWidget().screenGeometry()
        self.resize(self.screenShape.width()-10, self.screenShape.height()-100)
        self.setMinimumWidth(1300)

        self.setWindowTitle("Your recommndations")
        sl = QtWidgets.QSlider(Qt.Horizontal)
        sl.setMinimum(1)
        sl.setMaximum(10)
        sl.setTickInterval(1)
        sl.setTickPosition(QtWidgets.QSlider.TicksBelow)

        self.title = QtWidgets.QLabel("Your recommendations:")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName('title')

        self.yourID=QtWidgets.QLabel("Your login: "+getLogin(self.UserID))
        self.yourID.setWordWrap(True)
        self.yourID.setFixedSize(100,45)
        self.yourID.setObjectName("id")
        self.my_rates=QtWidgets.QPushButton('My rates')
        self.my_rates.setFixedSize(100,30)
        self.all_films=QtWidgets.QPushButton('All films')
        self.all_films.setFixedSize(100, 30)
        self.update = QtWidgets.QPushButton('Update')
        self.update.setFixedSize(100, 30)
        self.randomFilm = QtWidgets.QPushButton('Random \n film')
        self.randomFilm.setFixedSize(100, 70)
        self.my_rates.clicked.connect(lambda: self.btn_click(self.my_rates))
        self.all_films.clicked.connect(lambda: self.btn_click(self.all_films))
        self.update.clicked.connect(lambda: self.btn_click(self.update))
        self.randomFilm.clicked.connect(lambda: self.btn_click(self.randomFilm))

        self.splitterV = QSplitter(Qt.Vertical)

        self.films=Films(self.UserID,self.selected)
        self.main_widget = QWidget()
        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.main_layout.setSpacing(5)
        self.main_layout.addWidget(self.yourID,0,0)
        self.main_layout.addWidget(self.all_films,1,0)
        self.main_layout.addWidget(self.my_rates,2,0)
        self.main_layout.addWidget(self.update,3,0)
        self.main_layout.addWidget(self.randomFilm, 4, 0)
        self.main_widget.setObjectName('main')

        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidget(self.films)
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.setFrameShape(QFrame.NoFrame)

        #self.main_layout.addWidget(self.auto)
        #self.main_layout.addWidget(self.films)
        #self.main_layout.addWidget(self.btn_widget)
        self.main_layout.addWidget(self.splitterV,0,1,15,1)

        self.splitterV.addWidget(self.title)
        self.splitterV.addWidget(self.scrollWidget)
        self.splitterV.setHandleWidth(1)

        self.setCentralWidget(self.main_widget)

        self.setStyleSheet("""
                    #main{background-image: url(images/back1.jpg);background-attachment: fixed;}
                    QScrollArea { background: transparent; }
                    QScrollArea > QWidget > QWidget { background: transparent; }
                    #id{font:15px;color:white;}
                    QPushButton {font:20px;
                                width: 70px;
                                height: 30px;
                                color:white;
                                background-color:rgba(0,0,0,0.3);}
                    #title, #inform {font: 20px; color:white;
                            background-color:rgba(0,0,0,0.3);}
                    #style-label{font: 20px; color:white;}

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
    def get_random_film(self):
        print('Мы в функции get_random_film')
        connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
        cursor = connection.cursor()
        sql="SELECT movieID FROM movies"
        cursor.execute(sql)
        countMovies = cursor.rowcount
        print(countMovies)
        randomFilm = random.randint(1, countMovies)
        print(randomFilm)
        print('randomFilm: '+str(randomFilm))

        sql = "SELECT `movies`.`Title`,`movies`.`Year`,`links`.`Image`,`links`.`ImbdRate`,`movies`.`MovieID`, `movies`.`AllGanres` " \
              "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` WHERE `links`.`id`=%s "
        cursor.execute(sql, (int(randomFilm),))
        films=cursor.fetchone()
        movies=[]
        movies.append(films)
        return movies

    def btn_click(self,b):
        if b.text()=='My rates':
            self.dialog = MyRatings(self.UserID,self.selected)
            self.dialog.show()
        if b.text()=='All films':
            self.dialog = AllFilms(self.UserID,self.selected)
            self.dialog.show()
        if b.text()=='Update':
            sip.delete(self.films)
            self.films = Films(self.UserID,self.selected)
            self.scrollWidget.setWidget(self.films)
        if b.text() == 'Random \n film':
            print('Кнопка нажата')
            sip.delete(self.films)
            self.films = QWidget()
            self.films_layout=QtWidgets.QVBoxLayout(self.films)
            self.scrollWidget.setWidget(self.films)
            self.films.setObjectName('main')
            print('Создано новое окно')
            movie = self.get_random_film()
            self.myRateRandFilm = getRates(self.UserID, movie)
            self.widgetRandomFilm = QWidget()
            title = QtWidgets.QLabel(movie[0][0] + " (" + str(movie[0][1]) + ")")
            title.setObjectName('style-label')
            imdb = QtWidgets.QLabel("Imdb: " + str(movie[0][3]))
            ganres = QtWidgets.QLabel(movie[0][5].replace("|", ", "))
            ganres.setWordWrap(True)
            title.setWordWrap(True)
            imdb.setObjectName('style-label')
            ganres.setObjectName('style-label')
            im = QtWidgets.QLabel()
            im.setObjectName('style-label')
            data = urllib.request.urlopen(movie[0][2]).read()  # считали ссылку
            image = QtGui.QImage()
            image.loadFromData(data)
            wid = image.width()
            hei = image.height()
            pixmap = QtGui.QPixmap(image)
            pixmap = pixmap.scaled(wid, hei)
            im.setPixmap(pixmap)
            im.setFixedSize(wid, hei)
            self.width = pixmap.width()
            yourRating = QWidget()
            yourRating_layout = QtWidgets.QHBoxLayout(yourRating)
            rating_label = QtWidgets.QLabel('Your rate:')
            rating_label.setObjectName('style-label')
            rating_value = QtWidgets.QLabel(str(self.myRateRandFilm[0]))
            rating_value.setObjectName('style-label')
            yourRating_layout.addWidget(rating_label)
            yourRating_layout.addWidget(rating_value)
            rates = QWidget()
            rates_layout = QtWidgets.QHBoxLayout(rates)
            rates_layout.addWidget(imdb)
            rates_layout.setSpacing(5)
            inform = QWidget()
            imform_layout = QtWidgets.QVBoxLayout(inform)
            self.films_layout.addWidget(im)
            imform_layout.addWidget(title)
            imform_layout.addWidget(ganres)
            imform_layout.addWidget(rates)
            imform_layout.addWidget(yourRating)
            imform_layout.setSpacing(1)
            imform_layout.addStretch(1)
            self.films_layout.addWidget(inform)
            inform.setFixedWidth(self.width)
            inform.setObjectName("inform")
            '''self.setStyleSheet("""
                            #main{background-image: url(images/back1.jpg);background-attachment: fixed;}
                            #style-label{color:white;
                                    font:15px;}
                            #title,#inform{background-color:rgba(0,0,0,0.3);
                            QPushButton {font:20px;
                                width: 70px;
                                height: 30px;
                                color:white;
                                background-color:rgba(0,0,0,0.3);}
                            }
                        """)'''
            print('Всё ок7')

