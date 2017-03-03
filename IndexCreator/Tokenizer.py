import bs4
from bs4 import BeautifulSoup
import os
import re

from IndexCreator.MYSQLConnector import MYSQLConnector
from IndexCreator.Page import Page
from stemming.porter2 import stem

from IndexCreator.WordObject import WordObject


class Tokenizer:
    def __init__(self):
        self.path_to_resources = 'resources/WEBPAGES_RAW'
        self.stop_words = []
        self.bookkeeping = {}
        self.counter = 0
        self.all_words = {}  # cumulative across all files, mapping of string word to WordObject
        self.number_of_pages = 0
        self.mysql_connector = MYSQLConnector()

    def init(self):
        self.mysql_connector.create_words_table()
        self.mysql_connector.create_pages_table()

        self.load_stop_words('stopwords.txt')
        self.load_bookkeeping('resources/WEBPAGES_RAW/bookkeeping.tsv')
        self.parse_files()

        print("\rUploading words...\n")

        page_count = self.mysql_connector.get_page_count()

        progress = 0
        for value in t.all_words.values():
            self.mysql_connector.upload_word(value, page_count)
            progress += 1
            print("\r Uploaded " + str(progress) + " / " + str(len(t.all_words)), end='')

        print("\rFinished uploading words!\n")

        # todo: calculate tf-idf score and put into pages table

    # from https://github.com/stanfordnlp/CoreNLP/blob/master/data/edu/stanford/nlp/patterns/surface/stopwords.txt
    def load_stop_words(self, filename):
        with open(filename) as file_object:
            for line in file_object:
                self.stop_words.append(line.strip())

    def load_bookkeeping(self, filename):
        with open(filename) as file_object:
            for line in file_object:
                parts = line.split("\t")
                self.bookkeeping[parts[0]] = parts[1]

    def get_title_tokens(self, page, soup):
        try:
            title_text = remove_non_alphanumeric_characters(soup.title.string.strip())
        except AttributeError:
            return

        print("\r" + page.id + " -> " + title_text, end='')

        page.words = {}

        for key in [stem(x.strip()) for x in title_text.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words]:
            if key in page.words:
                page.words[key]['title'].append(self.counter)
                self.counter += 1
            else:
                page.words[key] = {'title': [self.counter], 'header': [], 'body': [], 'tfidf': 0.0}
                self.counter += 1

    def get_header_tokens(self, page, soup):
        header_text = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            header_text.append(remove_non_alphanumeric_characters(tag.text))

        header_tokens = []
        for phrase in header_text:
            header_tokens.extend([stem(x.strip()) for x in phrase.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words])

        for key in header_tokens:
            if key in page.words:
                page.words[key]['header'].append(self.counter)
                self.counter += 1
            else:
                page.words[key] = {'title': [], 'header': [self.counter], 'body': [], 'tfidf': 0.0}
                self.counter += 1

    def get_body_tokens(self, page, soup):
        text = soup.findAll(text=True)
        visible_text = remove_invisible_text(text)
        for i in range(len(visible_text)):
            visible_text[i] = remove_non_alphanumeric_characters(visible_text[i])

        body_tokens = []
        for phrase in visible_text:
            body_tokens.extend([stem(x.strip()) for x in phrase.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words])

        for key in body_tokens:
            if key in page.words:
                page.words[key]['body'].append(self.counter)
                self.counter += 1
            else:
                page.words[key] = {'title': [], 'header': [], 'body': [self.counter], 'tfidf': 0.0}
                self.counter += 1

    def parse_files(self):
        for foldername in os.listdir(self.path_to_resources):
            if os.path.isdir(self.path_to_resources + "/" + foldername):  # should exclude bookkeeping files
                for filename in os.listdir(self.path_to_resources + "/" + foldername):
                    if not filename.startswith("."):
                        self.parse_tokens(self.path_to_resources + "/" + foldername + "/" + filename, foldername + "/" + filename)

    def parse_tokens(self, filepath, page_id):
        p = Page(page_id)
        p.url = self.bookkeeping[page_id]
        soup = BeautifulSoup(read_file_contents(filepath), 'html.parser')
        self.get_title_tokens(p, soup)
        self.get_header_tokens(p, soup)
        self.get_body_tokens(p, soup)

        p.word_count = self.counter + 1

        if len(p.words) > 0:
            self.append_words(p)
            self.number_of_pages += 1
            self.mysql_connector.upload_page(p)
            self.counter = 0

    def append_words(self, page):
        for word, positions in page.words.items():
            if word not in self.all_words:
                self.all_words[word] = WordObject(word)

            self.all_words[word].pages.append(page.id)


def read_file_contents(filepath):
    with open(filepath, 'r') as fileobject:
        return re.sub(r'<br\W*>', '\n', str.lower(fileobject.read()))


def remove_non_alphanumeric_characters(word):
    return re.sub(r'[^\w_]|_', ' ', word)


def remove_invisible_text(text):
    return [x for x in list(filter(visible, text))]


# modification from http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif isinstance(element, bs4.element.Comment):
        return False
    return True


if __name__ == '__main__':
    t = Tokenizer()
    t.init()
