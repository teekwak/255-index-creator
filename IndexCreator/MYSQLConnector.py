import math
from ast import literal_eval

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
            PAGES LONGTEXT,
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
            WORDS LONGTEXT
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

    def calculate_tfidf(self):
        print("Calculating TF-IDF")

        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        cursor = db.cursor()

        # create counter
        total_count = 0
        sql = """
            SELECT count(*) from Pages
        """
        try:
            cursor.execute(sql)
            for row in cursor:
                total_count = row[0]
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        # store all words in memory
        idf_dict = {}
        sql = """
            SELECT Word, idf FROM Words
        """
        try:
            cursor.execute(sql)
            for row in cursor:
                idf_dict[row[0]] = row[1]
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        # update each page's words entry
        current = 0
        sql = """
            SELECT * FROM Pages
        """
        try:
            cursor.execute(sql)
            for row in cursor:
                all_words = literal_eval(row[3])

                for word, positions in all_words.items():
                    count = len(positions['title']) + len(positions['header']) + len(positions['body'])
                    positions['tfidf'] = (count / row[2]) * idf_dict[word]

                values = {
                    'id': str(row[0]),
                    'words': str(all_words)
                }

                cursor2 = db.cursor()
                sql = """
                    UPDATE Pages SET WORDS="{words}" WHERE ID="{id}"
                """.format(**values)
                try:
                    cursor2.execute(sql)
                    db.commit()
                    current += 1
                    print("\rFinished " + str(current) + " / " + str(total_count), end='')
                except MySQLError as e:
                    print('Got error {!r}, errno is {}'.format(e, e.args[0]))
                    db.rollback()

        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        db.close()

    def rerank_by_tfidf(self):
        print("Reranking")

        db = pymysql.connect(host=self.hostname, user=self.username, passwd=self.password, db=self.database, charset=self.charset)
        word_cursor = db.cursor()

        total_count = 0
        sql = """
            SELECT count(*) FROM Words
        """
        try:
            word_cursor.execute(sql)
            for row in word_cursor:
                total_count = row[0]
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        current = 0
        sql = """
            SELECT * FROM Words
        """

        try:
            word_cursor.execute(sql)
            for word_row in word_cursor:
                pages = literal_eval(word_row[1])

                if len(pages) > 1:
                    tuple_list = []

                    # todo: too expensive!
                    for page in pages:
                        page_cursor = db.cursor()
                        page_cursor.execute("SELECT WORDS FROM Pages WHERE ID='{0}'".format(page))

                        for page_row in page_cursor:
                            page_words = literal_eval(page_row[0])
                            tuple_list.append((page, page_words[word_row[0]]['tfidf']))

                    tuple_list = sorted(tuple_list, key=lambda x: x[1], reverse=True)
                    sorted_list = [i[0] for i in tuple_list]

                    values = {
                        'sorted_list': str(sorted_list),
                        'word': str(word_row[0])
                    }

                    update_cursor = db.cursor()
                    sql = """
                        UPDATE Words SET PAGES="{sorted_list}" WHERE WORD="{word}"
                    """.format(**values)
                    try:
                        update_cursor.execute(sql)
                        db.commit()
                        current += 1
                        print("\rFinished " + str(current) + " / " + str(total_count), end='')
                    except MySQLError as e:
                        print('Got error {!r}, errno is {}'.format(e, e.args[0]))
                        db.rollback()

        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback()

        db.close()


if __name__ == '__main__':
    m = MYSQLConnector()
    m.rerank_by_tfidf()