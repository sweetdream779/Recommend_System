import pymysql
import random

def getNik(n):
    array_a = ['e', 'y', 'u', 'i', 'o', 'a']
    array_b = ['q', 'w', 'r', 't', 'p', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n','m']
    connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
    cursor = connection.cursor()
    while(True):
        a = []
        b = []
        for i in range(n):
            k=random.randint(0, 5)
            a.append(array_a[k])
            r=random.randint(0, 19)
            b.append(array_b[r])
        name=''
        k=0
        r=0
        for i in range(2*n):
            if i%2==0:
                name=name+b[k]
                k=k+1
            else:
                name = name + a[r]
                r=r+1
        sql = "SELECT `Name` FROM `users` WHERE `Name`=%s"
        cursor.execute(sql,(name,))
        if cursor.rowcount==0:
            break
    print(name)
    cursor.close()
    connection.close()
    return name

def getPassword(n):
    array = ['e', 'y', 'u', 'i', 'o', 'a','q', 'w', 'r', 't', 'p', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
    pswd=''
    for i in range(n):
        k = random.randint(0, 25)
        pswd=pswd+array[k]
    return pswd


connection = pymysql.connect(host='localhost', user='root', passwd='', db='movies')
cursor = connection.cursor()
"""for i in range(1,691):
    while(True):
        n=random.randint(4, 10)
        if n%2==0:
            break
    name=getNik(n)
    sql = "INSERT INTO `users` (`UserID`,`Name`) VALUES (%s,%s)"
    cursor.execute(sql, (int(i),name))
    connection.commit()"""

for i in range(1,691):
    n=random.randint(5, 10)
    pswd=getPassword(n)
    sql="UPDATE `users` SET `Password`=%s WHERE `UserID`=%s"
    cursor.execute(sql, (pswd,int(i)))
    connection.commit()