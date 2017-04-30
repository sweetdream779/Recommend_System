import pymysql
import math
import numpy as np
import csv
from scipy.optimize import fmin_cg, minimize,check_grad

def get_n_records(n):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor=connection.cursor()
    cursor2=connection.cursor()
    sql="SELECT * FROM `ratings`"
    cursor.execute(sql)
    mentions = dict()
    count=0
    i=0
    while i<n:
        result = cursor.fetchone()
        userID=result[0]
        bookID=result[1]
        rate=result[2]
        if(rate==0):
            continue
        sql2="SELECT `Book-Title` FROM `bx-books` WHERE `ISBN`=%s"
        cursor2.execute(sql2,(bookID,))
        result2 = cursor2.fetchone()
        if (result2 is None):
            continue
        bookTitle=result2[0]
        i+=1
        if not userID in mentions:
            mentions[userID] = dict()
        mentions[userID][bookTitle] = rate
    cursor2.close()
    cursor.close()
    connection.close()
    return mentions

#КОСИНУСНАЯ МЕРА
def distCosine (vecA, vecB):
    def dotProduct (vecA, vecB):
        d = 0.0
        for dim in vecA:
            if dim in vecB:
                d += vecA[dim]*vecB[dim]
        return d
    return dotProduct (vecA,vecB) / math.sqrt(dotProduct(vecA,vecA)) / math.sqrt(dotProduct(vecB,vecB))

#print(get_n_records(20))

def getX(num_films):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    sql1 = "SELECT * FROM `movies`"
    #20 признаков + тэг?? + год??
    cursor.execute(sql1)
    num_movies = cursor.rowcount
    #if num_movies>num_films:
    #    num_movies=num_films
    X = np.zeros((num_movies,19), dtype=np.uint8)
    j = 0
    for m in cursor:
        for i in range(19):
            X[j,i]=m[i+4]
        j=j+1
        #if j==num_films:
        #   break
    np.savetxt('X.txt', X, fmt='%d')
    return X

def getRY(num_films, num_user):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor1 = connection.cursor()
    cursor2 =connection.cursor()
    cursor3 =connection.cursor()
    sql1="SELECT DISTINCT `UserID` FROM `ratings`"
    sql2="SELECT * FROM `movies`"
    cursor1.execute(sql1)
    num_users=cursor1.rowcount
    #if num_users>num_user:
    #    num_users=num_user
    cursor2.execute(sql2)
    num_movies=cursor2.rowcount
    #if num_movies>num_films:
    #    num_movies=num_films
    print(num_movies,num_users)
    R=np.zeros((num_movies,num_users),dtype=np.uint8)
    Y = np.zeros((num_movies,num_users), dtype=np.dtype("f2"))
    movies_titles=[]
    for nb in range(num_movies):
        movie=cursor2.fetchone()
        movieID=movie[0]
        movies_titles.append(movie[1])
        i=0
        #l1=""
        #l2=""
        cursor1.execute(sql1)
        for nu in cursor1:
            userID=nu[0]
            sql3="SELECT `Rating` from `ratings` WHERE `UserID` = %s and `MovieID` = %s"
            cursor3.execute(sql3,(userID,movieID))
            rate=cursor3.fetchone()
            if (not rate is None):
                R[nb,i]=1
                Y[nb,i]=rate[0]
            #l1=l1+str(R[nb,i])
            #l2=l2+str(Y[nb,i])
            i=i+1
            #if i==num_users:
            #    break
        print(nb)
        cursor1.close()
        cursor1 = connection.cursor()
        #f1.write(l1)
        #f1.write('\n')
        #f2.write(l2)
        #f2.write('\n')
    cursor1.close()
    cursor2.close()
    cursor3.close()
    connection.close()

    return R,Y, movies_titles,num_users,num_movies

def ReadFile(filename="<csv_file_location>"):
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    f = open(filename)
    r = csv.reader(f)
    i=0
    for line in r:
        i+=1
        if (i == 1):
            continue
        user = int(line[0])
        product = int(line[1])
        rate = float(line[2])
        sql = "INSERT INTO `ratings` (`UserID`, `MovieID`, `Rating`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user,product,rate))
        connection.commit()
    f.close()
    cursor.close()
    connection.close()

def Tags():
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    filename="tags.csv"
    f = open(filename)
    r = csv.reader(f)
    i = 0
    for line in r:
        i += 1
        if (i == 1):
            continue
        userID=int(line[0])
        movieID=int(line[1])
        tag=line[2]
        sql = "INSERT INTO `tags` (`UserID`, `MovieID`, `Tag`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (userID, movieID, tag))
        connection.commit()
    f.close()
    cursor.close()
    connection.close()

def Ganres():
    filename="movies.csv"
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    f = open(filename)
    r = csv.reader(f)
    i = 0
    allGanres = ['(no genres listed)', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary',
                 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX', 'Musical', 'Mystery','Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    currentValues=()
    maxlen=0
    for line in r:
        i += 1
        if (i ==1):
            continue
        if('"' in line[0]):
            line1=line[0].split('"')
            id = int(line1[0][0:-1])
            title=line1[1][0:-7]
            year = int(line1[1][-5:-1])
            ganre = line1[2][1:len(line1[2])]
        else:
            id=int(line[0])
            title=line[1][0:-7]
            year=int(line[1][-5:-1])
            ganre=line[2]
        ganres=ganre.split("|")
        currentValues=(id,title,year)
        for j in range(len(allGanres)):
            if (allGanres[j] in ganres):
                currentValues=currentValues+(True,)
            else:
                currentValues = currentValues +(False,)
        currentValues = currentValues +(ganre,)
        print(currentValues)
        sql = "INSERT INTO `movies` (`MovieID`, `Title`, `Year`, `(no genres listed)`, `Action`, `Adventure`, `Animation`, `Children`, `Comedy`,`Crime`, `Documentary`, `Drama`, `Fantasy`,`Film-Noir`, `Horror`, `IMAX`, `Musical`, `Mystery`,`Romance`, `Sci-Fi`, `Thriller`, `War`, `Western`, `AllGanres`) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)"
        cursor.execute(sql, currentValues)
        connection.commit()
    f.close()
    cursor.close()
    connection.close()

def Links():
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    filename = "links.csv"
    f = open(filename)
    r = csv.reader(f)
    i = 0
    for line in r:
        i += 1
        if (i == 1):
            continue
        ImdbID = int(line[1])
        movieID = int(line[0])
        if(line[2] == ""):
            tmdbID='NULL'
        else: tmdbID = int(line[2])
        sql = "INSERT INTO `links` (`MovieID`, `ImdbID`, `TmdbID`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (movieID, ImdbID, tmdbID))
        connection.commit()
    f.close()
    cursor.close()
    connection.close()

def CreateDB():
    ReadFile('ratings.csv')
    Tags()
    Links()
    Ganres()

def costFunc(Theta, Lambda,num_users,R,X,Y):
    #Lambda = args[0]
    #num_users = args[1]
    #R = args[2]
    #X = args[3]
    #Y = args[4]
    Theta = Theta.reshape(num_users,19)
    J = np.sum((np.dot(Theta, X.T) - Y.T) ** 2 * R.T) / 2
    # Regularization
    J = J + sum(sum(Theta.T ** 2)) * Lambda / 2
    return J

def gradFunc(Theta, Lambda,num_users,R,X,Y):
    #Lambda = args[0]
    #num_users = args[1]
    #R = args[2]
    #X = args[3]
    #Y = args[4]
    Theta = Theta.reshape(num_users, 19)
    Theta_grad = np.zeros(Theta.shape)
    for i in range(num_users):
        idx = np.where(R[:, i] == 1)[0]
        X_temp = X[idx, :]
        Y_temp = Y[idx, i]
        Theta_grad[i, :] = np.dot((np.dot(X_temp, Theta[i, :].T) - Y_temp).T, X_temp)+ Lambda * Theta[i, :]
    return Theta_grad.flatten()

def gradientDescent(Theta,alpha, maxiter, Lambda,num_users,R,X,Y):
    iter=0
    count=0
    #Lambda = args1[0]
    #num_users = args1[1]
    #R = args1[2]
    #X = args1[3]
    #Y = args1[4]
    #args=(Lambda,num_users,R,X,Y)
    while(True):
        Theta_old=Theta
        delta=gradFunc(Theta,Lambda,num_users,R,X,Y)
        Theta_new=Theta
        Theta_new=Theta_new-alpha*delta
        if(costFunc(Theta_new,Lambda,num_users,R,X,Y)<costFunc(Theta_old,Lambda,num_users,R,X,Y)):
            #print("###Step: "+str(iter)+", costFunc = "+str(costFunc(Theta_new,Lambda,num_users,R,X,Y)))
            count=0
            Theta=Theta_new
            iter=iter+1
            if costFunc(Theta_new,Lambda,num_users,R,X,Y) < 0.0000001:
                break
        else:
            count=count+1
            alpha=alpha/2
        if count>1000:
            print("Descent complete.")
            break
        if(iter>maxiter):
            print("Method diverges.")
            break
    return Theta, costFunc(Theta,Lambda,num_users,R,X,Y),iter

class ContentBased:
    #def __init__(self, num_train_films,num_train_users):
    #    self.num_train_films=num_train_films
    #    self.num_train_users=num_train_users
    def __init__(self):
        pass

    def getX(self):
        print("Getting X...")
        X=getX(self.num_train_films)
        self.X=X
        #return X

    def getRY(self):
        print("Getting R and Y...")
        (R,Y,movies_title,self.num_train_users, self.num_train_films)=getRY(self.num_train_films,self.num_train_users)
        self.Y=Y
        self.R=R
        #np.savetxt('Y.txt', self.Y, fmt='%d')
        #np.savetxt('R.txt', self.R, fmt='%f')
        self.movies_title=movies_title
        #return R,Y

    def read(self,file,shape,type=None):
        if type!=None:
            array=np.zeros(shape,dtype=type)
        else:
            array = np.zeros(shape)
        j = 0
        with open(file) as f:
            for line in f:
                mas = line.split(" ")
                for i in range(len(mas)):
                    if type==np.uint8:
                        s=mas[i].split('.')[0]
                        array[j][i] = int(s)
                    else:
                        array[j][i] = mas[i]
                j = j + 1
        return array

    def getRYX_file(self):
        connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
        cursor1 = connection.cursor()
        cursor2 = connection.cursor()
        sql1 = "SELECT DISTINCT `UserID` FROM `ratings`"
        sql2 = "SELECT * FROM `movies`"
        cursor1.execute(sql1)
        self.num_train_users = cursor1.rowcount
        cursor2.execute(sql2)
        self.num_train_films = cursor2.rowcount
        self.R=self.read('R.txt',(self.num_train_films, self.num_train_users),np.uint8)
        self.Y=self.read('Y.txt',(self.num_train_films, self.num_train_users),np.dtype("f2"))
        self.X=self.read('X.txt',(self.num_train_films, 19),np.uint8)
        self.Ymean=self.read('Ymean.txt',(self.num_train_films,1))
        self.Ynorm=self.read('Ynorm.txt',(self.num_train_films,self.num_train_users))

    def getTrainedTheta_file(self):
        self.trainedTheta=self.read('Theta.txt',(self.num_train_users, 19))

    def setInitialTheta(self):
        self.Theta=np.random.randn(self.num_train_users,19)

    def normalizeRatings(self):
        [m, n] = self.Y.shape
        self.Ymean = np.zeros((m, 1))
        self.Ynorm=np.zeros((m,n))
        for i in range(m):
            idx = np.where(self.R[i,:] == 1)
            if idx[0].shape==(0,):
                self.Ymean[i]=0
            else:
                self.Ymean[i] = np.mean(self.Y[i, idx])
            self.Ynorm[i, idx] = self.Y[i, idx] - self.Ymean[i]
        np.savetxt('Ymean.txt', self.Ymean, fmt='%f')
        np.savetxt('Ynorm.txt', self.Ynorm, fmt='%f')
        #print(self.Ymean)
        #print(self.Ynorm)

    def train(self):
        self.getX()
        self.getRY()
        self.setInitialTheta()
        Lambda = 10
        Theta0=self.Theta.flatten()
        print("Training...")
        args = (Lambda,self.num_train_users,self.R,self.X,self.Y)
        opts = {#'maxiter': None,  # default value.
               'disp': True,  # non-default value.
               'gtol': 1e-16,  # default value.
                #'norm': np.inf,  # default value.
                'eps': 1.4901161193847656e-08 # default value.
                }
        print("------------Minimize--------------")
        res = minimize(costFunc, Theta0, jac=gradFunc,args=args,
                                method = 'CG', options = opts)
        print((res.x).reshape(self.num_train_users,19))
        alpha=0.01
        maxiter=1000
        (theta, fun,iter)=gradientDescent(Theta0,alpha,maxiter, Lambda,self.num_train_users,self.R,self.X,self.Y)
        print("------------MyGradientDescent--------------")
        print("Iter = "+ str(iter)+"; Fun = "+ str(fun)+ "; Theta:")
        self.trainedTheta=theta.reshape(self.num_train_users,19)
        np.savetxt('Theta.txt', self.trainedTheta, fmt='%f')
        self.normalizeRatings()
        print(self.trainedTheta)

    def getPredictions(self,nomberOfUser, nom_pred):
        self.getRYX_file()
        self.getTrainedTheta_file()
        theta=self.trainedTheta[nomberOfUser,:]
        p=np.dot(self.X,theta.reshape(19,1))+self.Ymean#num_moviesx1
        withoutRate=np.where(self.R.T[nomberOfUser,:]==0)#num_mov_without_ratex1
        #print(withoutRate[0])
        this_pred=p.reshape(1,self.num_train_films)
        idx=np.argsort(this_pred[0])[::-1]
        #print(this_pred[0])
        #print(idx)
        num=0
        i=0
        ids=[]
        while num <nom_pred:
            if i>=self.num_train_films:
                break
            j=idx[i]
            if this_pred[0][j]<1:#никто не смотрел эти фильмы
                break
            if(j in withoutRate[0]):
                #print('Predicting for '+str(nomberOfUser)+' user rating '+str(this_pred[0][j])+ ' for movie ' +
                #          #str(self.movies_title[j])+
                #            "("+str(j)+")")
                ids.append(j)
                num=num+1
            #if(not j in withoutRate[0]):
                #print("Check: "+ str(this_pred[0][j])+ " and "+str(self.Y[j,nomberOfUser]))
            i=i+1
        return ids

#contentBased=ContentBased()
#contentBased.train()
#ids=contentBased.getPredictions(4,15)
#print(ids)
