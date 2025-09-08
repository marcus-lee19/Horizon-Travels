import mysql.connector
from mysql.connector import errorcode

hostname = '127.0.0.1'
username = 'root'
passwd = "Klk@1922001"
port = 3306
def getConnection():
    try:
        conn = mysql.connector.connect(host=hostname, user=username, password=passwd, port =port)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
            
    else:
        return conn
    
#Student ID : 24017967
#Student Name : Marcus Lee
#Student Email : kun2.lee@live.uwe.ac.uk