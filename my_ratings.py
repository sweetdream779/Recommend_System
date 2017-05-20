import pymysql
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QWidget,QFrame,QScrollArea,QVBoxLayout,QHBoxLayout,QLabel,QGridLayout,QMainWindow, QDesktopWidget)
from PyQt5.QtGui import QFont
import urllib.request

def getLogin(UserID):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    sql="SELECT `Name` FROM `users` WHERE `UserID`=%s"
    cursor.execute(sql, (int(UserID),))
    name = cursor.fetchone()[0]
    return name

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


class MyRatings(QMainWindow):
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!self.UserID = id
    def __init__(self,id,selected):
        super().__init__()
        self.UserID=id
        self.selected=selected
        self.initUI()

    def initUI(self):
        self.screenShape = QDesktopWidget().screenGeometry()
        self.resize(self.screenShape.width() - 10, self.screenShape.height() - 100)
        self.setMinimumWidth(1300)
#-----------------------------------------------------------------------------------------0
        self.LabelID = QLabel("Your ID: "+getLogin(self.UserID))
        self.LabelID.setFixedSize(300,30)
        self.LabelID.setObjectName("l")

        self.Label1 = QLabel("Number of films you have estemated: ")
        self.Label2 = QLabel("0")
        count = NumberEstemated(self.UserID)
        self.Label2.setText(str(count))

        self.LabelWidget=QWidget()
        self.LabelLayout = QHBoxLayout(self.LabelWidget)
        self.LabelLayout.addWidget(self.Label1)#-------------------------------------------2
        self.LabelLayout.addWidget(self.Label2)
        self.LabelWidget.setFixedSize(300,30)
        self.Label1.setObjectName("Label1")
        self.Label2.setObjectName("Label2")

        self.header = QLabel("My estimates")#---------------------------------------------------1
        self.header.setObjectName('style-label')
        self.header.setFont(QFont('SansSerif', 12))
        self.mainWindow = QWidget()
        self.mainWindow.setObjectName('mainWindow')
        self.filmsWindow = QGridLayout(self.mainWindow)
        self.filmsWindow.setSpacing(10)
        self.filmsWindow.setObjectName('filmsWindow')

        # SCROL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.main_widget = QWidget()
        self.main_widget.setObjectName('main')
        self.grid = QGridLayout(self.main_widget)
        self.grid.setContentsMargins(15, 15, 15, 15)
        self.grid.setSpacing(10)
        self.grid.addWidget(self.LabelID, 0, 0)
        self.grid.addWidget(self.header, 1, 0)
        self.grid.addWidget(self.LabelWidget, 2, 0)
        self.grid.addWidget(self.mainWindow, 3, 0)
        self.setLayout(self.grid)

        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidget(self.main_widget)
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.setFrameShape(QFrame.NoFrame)

        self.header.setFixedHeight(35)
        self.header.setAlignment(Qt.AlignCenter)
        self.setWindowTitle('My estimates')
        self.setWindowIcon(QIcon('2.png'))

        self.setCentralWidget(self.scrollWidget)
        self.setStyleSheet("""

                                   QLabel{color:white;
                                    font:15px;}
                                   #inform{background-color:rgba(0,0,0,0.3);}
                                   #main, #main_window {background-image: url(images/back1.jpg);background-attachment: fixed;}
                                   QSplitter::handle{background-color: transparent;}
                                   #style-label{
                                   font:18px;
                                       width: 55px;
                                       height: 18px;
                                       color:white;
                                   }
                                   #Label1,#Label2,#l{
                                   color:white;
                                   font:15px;
                                   }
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
        self.run=self.showFilms()


    def print_imgs(self,films):
        self.myRates = getRates(self.UserID, films)
        j = -2
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
    def showFilms(self):
        connection = pymysql.connect(host="localhost", user="root",
                                     passwd="", db="movies")
        cursor = connection.cursor()
        sql1 = "SELECT `MovieID` FROM `ratings` WHERE `UserID`=%s"
        cursor.execute(sql1, (int(self.UserID),))
        ids = []
        for id in cursor:
            ids.append(id[0])
        movies = []
        i = 0
        for id in ids:
            sql2 = "SELECT `movies`.`Title`,`movies`.`Year`,`links`.`Image`,`links`.`ImbdRate`,`movies`.`MovieID`, `movies`.`AllGanres` " \
                   "FROM `links` JOIN `movies` ON `links`.`MovieID`=`movies`.`MovieID`  WHERE `movies`.`MovieID`=%s"
            cursor.execute(sql2, (int(id),))
            films = cursor.fetchone()
            movies.append([])
            # Title,Year,Image,ImdbRate
            movies[i].append(films[0])
            movies[i].append(films[1])
            movies[i].append(films[2])
            movies[i].append(films[3])
            movies[i].append(films[4])
            movies[i].append(films[5])
            i = i + 1
        cursor.close()
        connection.close()
        self.print_imgs(movies)
