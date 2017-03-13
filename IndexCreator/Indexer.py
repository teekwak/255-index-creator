from IndexCreator.MYSQLConnector import MYSQLConnector
from IndexCreator.Tokenizer import Tokenizer


class Indexer:
    def __init__(self):
        pass

    @staticmethod
    def create_index():
        t = Tokenizer()
        t.init()

    @staticmethod
    def calculate_tfidf():
        m = MYSQLConnector()
        m.calculate_tfidf()

    @staticmethod
    def rerank():
        m = MYSQLConnector()
        m.rerank_by_tfidf()

    @staticmethod
    def create_redis():
        pass


# entry point
if __name__ == '__main__':
    # Indexer.create_index()
    # Indexer.calculate_tfidf()

    Indexer.create_redis();