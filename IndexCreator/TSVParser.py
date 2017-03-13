import json
import re
import redis

from IndexCreator.Tokenizer import Tokenizer


class TSVParser:
    def __init__(self):
        self.words = {}
        self.pages = {}

    def load_words(self):
        with open('resources/Words.tsv') as fileobject:
            print('\rLoading words', end='')
            for line in fileobject:
                splitAtTab = line.split("\t")
                self.words[splitAtTab[0].replace('\"', '')] = [(x, 0) for x in re.sub(r'[\[\]\"\']', '', splitAtTab[1]).split(", ")]

        print('\rLoaded words')

    def load_pages(self):
        with open('resources/PageWords.tsv') as fileobject:
            print('\rLoading pages', end='')
            for line in fileobject:
                splitAtTab = line.split("\t")
                self.pages[splitAtTab[0].replace("\"", "")] = json.loads(splitAtTab[1].replace('"', '').replace("'", '"'))
        print('\rLoaded pages')

    def add_tfidf(self):
        counter = 0

        for word, tuples in self.words.items():
            for i in range(len(tuples)):
                tuples[i] = (tuples[i][0], self.pages[tuples[i][0]][word]['tfidf'])

            counter += 1
            print('\rCompleted ' + str(counter) + ' words', end='')

        print('\rCompleted adding tfidf!')


    def rerank_pages(self):
        for word, tuples in self.words.items():
            self.words[word] = sorted(tuples, key=lambda x: x[1], reverse=True)

    def upload_to_redis(self):
        counter = 0
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        for word, tuples in self.words.items():
            r.rpush(word, *tuples)

            counter += 1
            print('\rPushed ' + str(counter) + ' words', end='')

        print('\rCompleted pushing to Redis!\n')


if __name__ == '__main__':
    t = TSVParser()
    t.load_words()
    t.load_pages()

    t.add_tfidf()
    t.upload_to_redis()
    t.rerank_pages()

    print("PROCESS COMPLETED!!!")