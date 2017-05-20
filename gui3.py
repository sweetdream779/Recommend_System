import sys, os, math,numpy as np
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication,QMainWindow, QAction,QSplitter,\
    QGraphicsDropShadowEffect,QSizePolicy,QScrollArea,QFrame,QSizePolicy
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import Qt,QSize,QMargins
#import first.py
import pymysql
from PyQt5.QtGui import QImage, QPalette, QBrush, QColor
import urllib.request
import sip
from  functools import partial
from ratingWidget import RatingWidget

def getLogin(UserID):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    sql="SELECT `Name` FROM `users` WHERE `UserID`=%s"
    cursor.execute(sql, (int(UserID),))
    name = cursor.fetchone()[0]
    return name

def getFilms(mode,ganre,film=None):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    if film is None:
        if ganre=='all':
            if mode=='normal':
                sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID`"
            if mode=='rate':
                sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` ORDER BY `ImbdRate` DESC"
            if mode=='year':
                sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID`" \
                      "ORDER BY `Year` DESC"
            cursor.execute(sql)
        else:
            if mode == 'normal':
                sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` " \
                      "WHERE `movies`.`"+str(ganre)+"`=1"
            if mode == 'rate':
                sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` " \
                      "WHERE `movies`.`" + str(ganre) + "`=1 ORDER BY `ImbdRate` DESC"
            if mode=='year':
                sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                      "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` " \
                      "WHERE `movies`.`" + str(ganre) + "`=1 ORDER BY `Year` DESC"
            cursor.execute(sql)
    else:
        sql = "SELECT `links`.`Image`,`links`.`ImbdRate`,`movies`.`Title`,`movies`.`Year`,`movies`.`MovieID`, `movies`.`AllGanres` " \
              "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID` WHERE `Title` LIKE %s"
        cursor.execute(sql,('%'+film+'%',))
        if cursor.rowcount==0:
            return None,0
    movies=[]
    num=cursor.rowcount
    i=0
    for im in cursor:
        movies.append([])
        #Title,Year,Image,ImdbRate,Ganres
        movies[i].append(im[2])
        movies[i].append(im[3])
        movies[i].append(im[0])
        movies[i].append(im[1])
        movies[i].append(im[4])
        movies[i].append(im[5])
        i=i+1
    cursor.close()
    connection.close()
    return movies, num

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

class Films(QWidget):
    def __init__(self,id,page,films,selected):
        super().__init__()
        self.UserID=id
        self.current_page=page
        self.films=films
        self.selected=selected
        self.initUI()

    def initUI(self):
        self.grid=QtWidgets.QGridLayout(self)
        self.setMinimumWidth(800)
        finish=self.current_page*20
        start=finish-20
        films = self.films[start:finish]
        self.myRates=getRates(self.UserID, films)
        self.print_imgs(films)
        self.grid.setSpacing(5)

    def print_imgs(self,films):
        j=-2
        self.bool = []
        for i in range(len(films)):
            ost=i%4
            if (ost==0):
                j=j+2
            w=QWidget()
            layout=QtWidgets.QGridLayout(w)
            layout.setSpacing(0)
            title=QtWidgets.QLabel(films[i][0]+" ("+str(films[i][1])+")")
            #title.setWordWrap(True)
            imdb=QtWidgets.QLabel("Imdb: "+str(films[i][3]))
            ganres = QtWidgets.QLabel(films[i][5].replace("|", ","))
            title.setWordWrap(True)
            ganres.setWordWrap(True)
            im = QtWidgets.QLabel()
            if(not self.selected):
                data = urllib.request.urlopen(films[i][2]).read()
                image = QtGui.QImage()
                image.loadFromData(data)
                wid = image.width()
                hei = image.height()
                pixmap = QtGui.QPixmap(image)
                #pixmap = pixmap.scaled(wid, hei)
                im.setPixmap(pixmap)
                im.setFixedSize(wid, hei)
                self.width = pixmap.width()
            else:
                self.width=182

            yourRating = QWidget()
            yourRating_layout = QtWidgets.QHBoxLayout(yourRating)
            rating_label = QtWidgets.QLabel('Your rate:')
            rating_value = QtWidgets.QLabel(str(self.myRates[i]))
            yourRating_layout.addWidget(rating_label)
            yourRating_layout.addWidget(rating_value)

            ratesImdb = QWidget()
            rates_layout = QtWidgets.QHBoxLayout(ratesImdb)
            rates_layout.addWidget(imdb)
            button = QtWidgets.QPushButton("Estimate")
            button.setFixedSize(70, 20)
            button.setStyleSheet("background-color:rgba(5,232,217,0.3); color:black; font:15px;")
            self.bool.append(False)
            button.clicked.connect(partial(self.estimate, films[i][4], j, ost, i,rating_value))
            rates_layout.addWidget(button)

            inform = QWidget()
            inform_layout = QtWidgets.QVBoxLayout(inform)
            layout.addWidget(im,0,0)
            inform_layout.addWidget(title)
            inform_layout.addWidget(ganres)
            inform_layout.addWidget(ratesImdb)
            inform_layout.addWidget(yourRating)
            layout.addWidget(inform,1,0)
            inform.setMaximumWidth(self.width)
            #inform.setMaximumHeight(150)
            inform.setObjectName("inform")
            self.grid.addWidget(w, j, ost)
            self.setStyleSheet("""
                            QLabel{color:white;
                                    font:14px;}
                            #inform{background-color:rgba(0,0,0,0.3);}
                        """)

    def estimate(self,movieID,row,col,j,rating_value):
        stars = QWidget()
        # print(b, j, self.bool)
        stars.setMinimumWidth(self.width)
        stars_layout = QtWidgets.QHBoxLayout(stars)
        stars_layout.setSpacing(0)
        for i in range(5):
            im = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap("rating2.png")
            im.setPixmap(pixmap)
            stars_layout.addWidget(im)
        #rating_value_widget = QtWidgets.QLabel('0')
        rating_widget = RatingWidget(num_icons=5)
        rating_widget.value_updated.connect(
            lambda value: self.setRating(str(value), movieID, rating_value)
        )
        rate_layout = QtWidgets.QHBoxLayout()
        rate_layout.addWidget(rating_widget)
        rate_widget = QtWidgets.QWidget()
        rate_widget.setMinimumWidth(self.width)
        rate_widget.setLayout(rate_layout)
        if self.bool[j] == False:
            self.grid.addWidget(stars, row + 1, col)
            self.bool[j] = True
            # layout.addWidget(rating_value_widget,3,0)
            self.grid.addWidget(rate_widget, row + 1, col)

    def setRating(self,value,movieID,rating_value):
        rating_value.setText(str(value))
        insertRate(self.UserID,movieID,value)

class AllFilms(QMainWindow):
    def __init__(self,id,selected):
        super().__init__()
        self.UserID=id
        self.selected=selected
        self.initUI()

    def initUI(self):
        self.screenShape = QtWidgets.QDesktopWidget().screenGeometry()
        self.resize(self.screenShape.width()-10, self.screenShape.height()-100)
        self.setMinimumWidth(1300)

        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.setStretch(0,1)

        self.notSortButton = QtWidgets.QPushButton("All movies")
        self.sortRateButton=QtWidgets.QPushButton("Sort by rating↓")
        self.sortYearButton = QtWidgets.QPushButton("Sort by year↓")
        self.notSortButton.setFixedSize(150,20)
        self.sortRateButton.setFixedSize(150,20)
        self.sortYearButton.setFixedSize(150,20)
        self.notSortButton.clicked.connect(self.change_mode)
        self.sortRateButton.clicked.connect(self.change_mode)
        self.sortYearButton.clicked.connect(self.change_mode)
        self.top_layout.addStretch(1)
        self.top_layout.insertWidget(0,self.notSortButton)
        self.top_layout.insertWidget(1,self.sortRateButton)
        self.top_layout.insertWidget(2,self.sortYearButton)

        self.searchEdit=QtWidgets.QLineEdit()
        self.searchEdit.setMinimumSize(500,30)
        self.findButton=QtWidgets.QPushButton("Find")
        self.findButton.setFixedSize(150,20)
        self.findButton.clicked.connect(self.btn_find)
        self.top_layout.insertWidget(3,self.searchEdit)
        self.top_layout.insertWidget(4,self.findButton)

        #self.splitterV = QSplitter(Qt.Vertical)
        self.splitter=QWidget()
        self.splitterV=QtWidgets.QVBoxLayout(self.splitter)

        self.currentPage = 1
        self.mode='normal'
        self.ganre='all'

        self.imgs, self.numFilms = getFilms(self.mode, self.ganre)

        self.central=Films(self.UserID,self.currentPage,self.imgs,self.selected)
        self.top=QWidget()
        self.top.setLayout(self.top_layout)
        self.left=QWidget()
        self.bottom = QWidget()
        self.bottom.setObjectName("bottom")

        self.main_widget = QWidget()
        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.main_widget.setObjectName('main')

        self.scrollWidget = QScrollArea()
        self.scrollWidget.setStyleSheet("background-color:transparent;")
        self.scrollWidget.setWidget(self.splitter)
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.setFrameShape(QFrame.NoFrame)

        self.splitterV.insertWidget(0,self.central)
        self.splitterV.insertWidget(1,self.bottom)
        self.ganres()
        self.main_layout.addWidget(self.top,0,1)
        self.main_layout.addWidget(self.scrollWidget,1,1,21,1)

        self.setCentralWidget(self.main_widget)

        self.numPages = math.ceil(self.numFilms / 20)
        self.pages(self.numPages)

        self.setStyleSheet("""
                            #main {background-image: url(images/back1.jpg);background-attachment: fixed;}
                            QSplitter::handle{background-color: transparent;}
                            QPushButton {font:15px;
                                width: 55px;
                                height: 18px;
                                color:white;
                                background-color:rgba(0,0,0,0.3);
                                border:1px solid rgba(0,0,0, 0.8);}
                            QLineEdit{border-radius: 2px;
                                    background-color:rgba(0,0,0,0.3);
                                    border: 1px solid rgba(255,255,255, 0.3);
                                    color:white;
                                    font:20px;}

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

    def pages(self,num_pages):
        self.bottom_layout = QtWidgets.QGridLayout(self.bottom)
        self.bottom_layout.setSpacing(0)
        self.bottom.setStyleSheet("""
                            QPushButton{font:15px;
                                width: 20px;
                                height: 18px;
                                color:white;
                                background-color:rgba(0,0,0,0.3);
                                border:1px solid rgba(255,255,255, 0.3);}
                            QLabel{color:white;
                                    font:20px;
                                    width:10px;}
                            """)

        if self.currentPage<5:
            for i in range(5):
                button = QtWidgets.QPushButton(str(i + 1))
                if i+1==self.currentPage:
                    button.setStyleSheet("background-color:white; color:black;")
                button.clicked.connect(self.change_page)
                self.bottom_layout.addWidget(button, 0, i)
            label=QtWidgets.QLabel('...')
            self.bottom_layout.addWidget(label, 0, 5)

            button = QtWidgets.QPushButton(str(num_pages))
            self.bottom_layout.addWidget(button, 0, 6)
            button.clicked.connect(self.change_page)

        elif self.currentPage>(num_pages-4):
            button = QtWidgets.QPushButton(str(1))
            self.bottom_layout.addWidget(button, 0, 0)
            button.clicked.connect(self.change_page)

            label = QtWidgets.QLabel('...')
            self.bottom_layout.addWidget(label, 0, 1)
            pgs=num_pages-4
            j=2
            while pgs<=num_pages:
                button = QtWidgets.QPushButton(str(pgs))
                if pgs==self.currentPage:
                    button.setStyleSheet("background-color:white; color:black;")
                button.clicked.connect(self.change_page)
                self.bottom_layout.addWidget(button, 0, j)
                pgs=pgs+1
                j=j+1

        else:
            button = QtWidgets.QPushButton(str(1))
            button.clicked.connect(self.change_page)
            self.bottom_layout.addWidget(button, 0, 0)

            label = QtWidgets.QLabel('...')
            self.bottom_layout.addWidget(label, 0, 1)

            button = QtWidgets.QPushButton(str(self.currentPage-1))
            button.clicked.connect(self.change_page)
            self.bottom_layout.addWidget(button, 0, 2)

            button = QtWidgets.QPushButton(str(self.currentPage))
            button.setStyleSheet("background-color:white; color:black;")
            button.clicked.connect(self.change_page)
            self.bottom_layout.addWidget(button, 0, 3)

            button = QtWidgets.QPushButton(str(self.currentPage+1))
            button.clicked.connect(self.change_page)
            self.bottom_layout.addWidget(button, 0, 4)

            label = QtWidgets.QLabel('...')
            self.bottom_layout.addWidget(label, 0, 5)

            button = QtWidgets.QPushButton(str(num_pages))
            button.clicked.connect(self.change_page)
            self.bottom_layout.addWidget(button, 0, 6)

    def btn_find(self):
        film=self.searchEdit.text()
        self.ganre="all"
        self.ganresL.setText("All ganres")
        if hasattr(self, 'bottom'):
            sip.delete(self.bottom)
            del self.bottom
        sip.delete(self.central)
        del self.central

        if hasattr(self, 'sortRateButton'):
            sip.delete(self.sortRateButton)
            del self.sortRateButton
            sip.delete(self.sortYearButton)
            del self.sortYearButton

        self.currentPage=1
        self.imgs, self.numFilms = getFilms(self.mode, self.ganre,film)
        if self.numFilms==0:
            self.central = QWidget()
            layout=QtWidgets.QHBoxLayout(self.central)
            message = QtWidgets.QLabel('There are no matches.')
            layout.addWidget(message)
            self.splitterV.insertWidget(0, self.central)
        else:
            self.numPages = math.ceil(self.numFilms / 20)
            self.central = Films(self.UserID, self.currentPage, self.imgs,self.selected)
            self.splitterV.insertWidget(0, self.central)
            if self.numPages>1:
                self.bottom = QWidget()
                self.splitterV.insertWidget(1, self.bottom)
                self.pages(self.numPages)

    def change_page(self):
        sender=self.sender()
        click_btn=sender.text()
        self.currentPage=int(click_btn)
        self.central.hide()
        self.central.deleteLater()
        del self.central
        self.central=Films(self.UserID,self.currentPage,self.imgs,self.selected)
        self.splitterV.insertWidget(0,self.central)
        sip.delete(self.bottom)
        del self.bottom
        self.bottom=QWidget()
        self.splitterV.insertWidget(1, self.bottom)
        self.pages(self.numPages)

    def change_mode(self):
        self.searchEdit.setText('')
        if not hasattr(self, 'sortRateButton'):
            self.sortRateButton = QtWidgets.QPushButton("Sort by rating↓")
            self.sortYearButton = QtWidgets.QPushButton("Sort by year↓")
            self.sortRateButton.clicked.connect(self.change_mode)
            self.sortYearButton.clicked.connect(self.change_mode)
            self.top_layout.insertWidget(1,self.sortRateButton)
            self.top_layout.insertWidget(2,self.sortYearButton)

        sender = self.sender()
        text = sender.text()
        self.currentPage=1
        if text=='All movies':
            self.mode='normal'
            self.ganresL.setText("All ganres")
            self.ganre="all"
        if text=="Sort by rating↓":
            self.mode='rate'
        if text=="Sort by year↓":
            self.mode='year'

        del self.imgs
        self.imgs, self.numFilms = getFilms(self.mode, self.ganre)
        self.numPages = math.ceil(self.numFilms / 20)

        #self.central.hide()
        #self.central.deleteLater()
        #del self.central
        sip.delete(self.central)
        self.central = Films(self.UserID, self.currentPage,self.imgs,self.selected)
        self.splitterV.insertWidget(0, self.central)

        if hasattr(self, 'bottom'):
            sip.delete(self.bottom)
        self.bottom = QWidget()
        self.splitterV.insertWidget(1, self.bottom)
        self.pages(self.numPages)

    def ganres(self):
        self.yourID = QtWidgets.QLabel("Your login: " + getLogin(self.UserID))
        self.yourID.setWordWrap(True)
        self.yourID.setFixedSize(100, 46)
        self.yourID.setObjectName("id")

        self.main_layout.addWidget(self.yourID, 0, 0)
        self.ganresL = QtWidgets.QLabel("All ganres")
        self.ganresL.setObjectName("ganresL")
        self.main_layout.addWidget(self.ganresL,1,0)
        allGanres=['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy','Film-Noir', 'Horror', 'IMAX', 'Musical', 'Mystery','Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
        allGanres.sort()

        for i in range(len(allGanres)):
            ganre=QtWidgets.QPushButton(allGanres[i])
            self.main_layout.addWidget(ganre,i+2,0)
            ganre.setFixedSize(150,20)
            ganre.clicked.connect(self.set_ganre)
        self.ganresL.setStyleSheet("""color:white;font:20px;""")
        self.yourID.setStyleSheet("""color:white;font:16px;""")

    def set_ganre(self):
        if not hasattr(self, 'sortRateButton'):
            self.sortRateButton = QtWidgets.QPushButton("Sort by rating↓")
            self.sortYearButton = QtWidgets.QPushButton("Sort by year↓")
            self.sortRateButton.clicked.connect(self.change_mode)
            self.sortYearButton.clicked.connect(self.change_mode)
            self.top_layout.insertWidget(1,self.sortRateButton)
            self.top_layout.insertWidget(2,self.sortYearButton)
        self.searchEdit.setText('')
        sender = self.sender()
        ganre = sender.text()
        self.ganresL.setText(ganre)

        self.currentPage = 1
        self.ganre=ganre

        self.imgs, self.numFilms = getFilms(self.mode, self.ganre)
        self.numPages = math.ceil(self.numFilms / 20)

        sip.delete(self.central)
        del self.central
        self.central = Films(self.UserID, self.currentPage,self.imgs,self.selected)
        self.splitterV.insertWidget(0, self.central)

        if hasattr(self, 'bottom'):
            sip.delete(self.bottom)
        self.bottom = QWidget()
        self.splitterV.insertWidget(1, self.bottom)
        self.pages(self.numPages)