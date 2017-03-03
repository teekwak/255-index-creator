import math
import pymysql
from pymysql import MySQLError


class MYSQLConnector:
    def __init__(self):
        self.hostname = 'localhost'
        self.username = 'root'
        self.password = 'password'
        self.database = 'search'
        self.charset = 'utf8'

    def create_words_table(self):
        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        cursor = db.cursor()

        sql = """
            CREATE TABLE IF NOT EXISTS Words(
            WORD TEXT,
            PAGES MEDIUMTEXT,
            IDF FLOAT
            ) CHARACTER SET utf8
        """

        cursor.execute(sql)
        db.close()

    def get_page_count(self):
        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        cursor = db.cursor()

        sql = """
            select count("ID") from PAGES
        """

        page_count = 0

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                page_count = row[0]
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        if page_count == 0:
            raise MySQLError('Number of pages in Pages table is 0')

        return page_count

    def upload_word(self, word_object, page_count):
        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        cursor = db.cursor()

        values = {
            'word': str(word_object.word),
            'pages': str(word_object.pages),
            'idf': str(math.log(page_count / len(word_object.pages)))
        }

        sql = """
            INSERT INTO Words (WORD, PAGES, IDF)
            VALUES ("{word}", "{pages}", "{idf}")
        """.format(**values)

        try:
            cursor.execute(sql)
            db.commit()
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        db.close()

        pass

    def create_pages_table(self):
        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        cursor = db.cursor()

        sql = """
            CREATE TABLE IF NOT EXISTS Pages(
            ID VARCHAR(255) UNIQUE,
            URL TEXT,
            WORD_COUNT INT,
            WORDS MEDIUMTEXT
            ) CHARACTER SET utf8
        """

        cursor.execute(sql)
        db.close()

    def upload_page(self, page):
        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        cursor = db.cursor()

        values = {
            'id': str(page.id),
            'url': str(page.url),
            'word_count': str(page.word_count),
            'words': str(page.words)
        }

        sql = """
            INSERT INTO Pages (ID, URL, WORD_COUNT, WORDS) VALUES ("{id}", "{url}", "{word_count}", "{words}")
        """.format(**values)

        try:
            cursor.execute(sql)
            db.commit()
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        db.close()

if __name__ == '__main__':
    m = MYSQLConnector()
    print("i do nothing")
