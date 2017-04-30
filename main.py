import pymysql
import math
class collaborative_filtering:
    def __init__(self, userID,nBestUsers=15, nBestProducts=15):
        self.userID=userID
        self.nBestUsers=nBestUsers
        self.nBestProducts=nBestProducts

    def ReadFile(self):
        try:
            conn = pymysql.connect(host="localhost", user="root",
                                   passwd="", db="movies")
        except pymysql.Error as err:
            print("Connection error: {}".format(err))
            conn.close()
        cursor = conn.cursor()
        # cur = conn.cursor(MySQLdb.cursors.DictCursor) DictCursor - чтобы данные возвращались, как словари
        # --------------------------------------------------------------------------------------------------------------
        mentions = dict()
        sql = """
            SELECT UserID, MovieID, Rating
            FROM ratings
        """
        cursor.execute(sql)
        data=cursor.fetchall()
        for row in data:
            user, product, rate = row
            if not user in mentions:
                mentions[user] = dict()
            mentions[user][product]=rate
        conn.close()
        return mentions

    def distCosine (self,vecA, vecB):
        def dotProduct (vecA, vecB):
            d = 0.0
            for dim in vecA:
                if dim in vecB:
                    d += vecA[dim]*vecB[dim]
            return d
        return dotProduct (vecA,vecB) / math.sqrt(dotProduct(vecA,vecA)) / math.sqrt(dotProduct(vecB,vecB))
    def makeRecommendation (self):
        userID = self.userID
        nBestUsers = self.nBestUsers
        nBestProducts = self.nBestProducts
        userRates=self.ReadFile()
        matches = [(u, self.distCosine(userRates[userID], userRates[u])) for u in userRates if u != userID]

        #упорядочиваем по мере
        bestMatches = sorted(matches, key=lambda item:item[1], reverse=True)[:nBestUsers]
        #print ("Most correlated with '%s' users:" % userID)
        #for line in bestMatches:
            #print( "  UserID: %6s  Coeff: %6.4f" % (line[0], line[1]))
        #итак, нашли пользователей, которые наиболее близки к рассматриваемому
        #--------------------------------------------------------------------------------------------------------
        sim = dict()
        sim_all = sum([x[1] for x in bestMatches])#сумма всех мер для всех близких пользователей

        #переводим данные близких пользователей и их мер в словарь---> пользователь:мера
        bestMatches = dict([x for x in bestMatches if x[1] > 0.0])

        for relatedUser in bestMatches:
            for product in userRates[relatedUser]:
                if not product in userRates[userID]:#проверяем, не оценивал ли данный фильм рассматриваемый пользователь
                    if not product in sim:
                        sim[product] = 0.0#добавили в словарь sim наш продукт
                    sim[product] += userRates[relatedUser][product] * bestMatches[relatedUser]
                    '''суммируем оценки каждого фильма (который не смотрел рассматриваемый пользователь), близкими
                     пользователями, умноженными на коэффициент корреляции'''

        for product in sim:
            sim[product] /= sim_all#делим суммируемые оценки на сумму мер корреляции всех близких пользователей
        bestProducts = sorted(sim.items(), key=lambda item:item[1], reverse=True)[:nBestProducts]
        #print ("Most correlated products:")
        ids=[]
        for prodInfo in bestProducts:
            ids.append(prodInfo[0])
            #print ("  ProductID: %6s " % (prodInfo[0]))
        return ids
#-----------------------------------------------------------------------------------------------------------------------------
