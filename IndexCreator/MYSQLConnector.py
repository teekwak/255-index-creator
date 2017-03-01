import pymysql


class MYSQLConnector:
    def __init__(self):
        self.hostname = 'localhost'
        self.username = 'root'
        self.password = 'password'
        self.database = 'search'


    def insert(self):
        pass

    def upload_page(self):
        pass










# db = pymysql.connect("localhost","root","password","search")
# cursor = db.cursor()
#
# sql = """CREATE TABLE EMPLOYEE (
#    FIRST_NAME  CHAR(20) NOT NULL,
#    LAST_NAME  CHAR(20),
#    AGE INT,
#    SEX CHAR(1),
#    INCOME FLOAT )"""
#
# cursor.execute(sql)
#
# sql = """INSERT INTO EMPLOYEE(FIRST_NAME,
#    LAST_NAME, AGE, SEX, INCOME)
#    VALUES ('Mac', 'Mohan', 20, 'M', 2000)"""
# try:
#    # Execute the SQL command
#    cursor.execute(sql)
#    # Commit your changes in the database
#    db.commit()
# except:
#    # Rollback in case there is any error
#    db.rollback()
#
# db.close()
