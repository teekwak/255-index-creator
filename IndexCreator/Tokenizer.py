import bs4
from bs4 import BeautifulSoup
import os
import re

from IndexCreator.Page import Page
from stemming.porter2 import stem

class Tokenizer:
    def __init__(self):
        self.path_to_resources = 'resources/WEBPAGES_RAW'
        self.stop_words = []
        self.bookkeeping = {}
        self.pages = [] # todo: populate this

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

        # print(page.id + " -> " + title_text)

        page.title_tokens = {}

        for key in [stem(x.strip()) for x in title_text.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words]:
            if key in page.title_tokens:
                page.title_tokens[key] += 1
            else:
                page.title_tokens[key] = 1

    def get_header_tokens(self, page, soup):
        header_text = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            header_text.append(remove_non_alphanumeric_characters(tag.text))

        header_tokens = []
        for phrase in header_text:
            header_tokens.extend([stem(x.strip()) for x in phrase.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words])

        for key in header_tokens:
            if key in page.header_tokens:
                page.header_tokens[key] += 1
            else:
                page.header_tokens[key] = 1

    def get_body_tokens(self, page, soup):
        text = soup.findAll(text=True)
        visible_text = remove_invisible_text(text)
        for i in range(len(visible_text)):
            visible_text[i] = remove_non_alphanumeric_characters(visible_text[i])

        body_tokens = []
        for phrase in visible_text:
            body_tokens.extend([stem(x.strip()) for x in phrase.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words])

        for key in body_tokens:
            if key in page.body_tokens:
                page.body_tokens[key] += 1
            else:
                page.body_tokens[key] = 1

        # page.body_tokens = self.remove_header_token_duplicates(page)

    def parse_files(self):
        for foldername in os.listdir(self.path_to_resources):
            if os.path.isdir(self.path_to_resources + "/" + foldername): # should exclude bookkeeping files
                if foldername == '0':
                    for filename in os.listdir(self.path_to_resources + "/" + foldername):
                        if filename == '4':
                            self.parse_tokens(self.path_to_resources + "/" + foldername + "/" + filename, foldername + "/" + filename)

    def parse_tokens(self, filepath, id):
        p = Page(id)
        p.url = self.bookkeeping[id]
        soup = BeautifulSoup(self.read_file_contents(filepath), 'html.parser')
        self.get_title_tokens(p, soup)
        self.get_header_tokens(p, soup)
        self.get_body_tokens(p, soup)
        self.pages.append(p)

    def read_file_contents(self, filepath):
        with open(filepath, 'r') as fileobject:
            return re.sub(r'<br\W*>', '\n', str.lower(fileobject.read()))

    # def remove_header_token_duplicates(self, page):
    #     temp_dict = page.body_tokens
    #
    #     for word in page.header_tokens:
    #         temp_dict[word] -= 1
    #
    #     to_delete = []
    #     for word in temp_dict:
    #         if temp_dict[word] == 0:
    #             to_delete.append(word)
    #
    #     for w in to_delete:
    #         temp_dict.pop(w, None)
    #
    #     return temp_dict


def remove_non_alphanumeric_characters(word):
    return re.sub(r'[^\w]', ' ', word)


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
    t.load_stop_words('stopwords.txt')
    t.load_bookkeeping('resources/WEBPAGES_RAW/bookkeeping.tsv')
    t.parse_files()

    # t.parse_tokens('test.txt', 'no id')
    # t.get_files()

    for page in t.pages:
        for key, value in page.title_tokens.items():
            print("title: " + key + " -> " + str(value))
        for key, value in page.header_tokens.items():
            print("header: " + key + " -> " + str(value))
        for key, value in page.body_tokens.items():
            print("body: " + key + " -> " + str(value))

    print('number of pages: ' + str(len(t.pages)))




    # todo: clean unclosed tags using the prettify function (see file 0-1)
    # todo: rewrite those files to a new resources directory?
    # todo: what to do about file 0-0 (the one with only numbers?
    # todo: make another class just to parse text (INCLUDES header tags, list tags, paragraph tags, etc)
    # todo: remove apostrophe s
    # todo: stemming? remove contractions

# todo: page table keys: page id, url, words

# {title: [ {x: 1, y: 2, z: 3} ], headers: [ {x: 1, y: 2, z: 3} ], body: [ {x: 1, y: 2, z: 3} ]}


# todo: word table keys: word, idf, page ids (as json)
# todo: how to make inverted index
# todo: parse a file
# todo: if value exists in table
# todo: update value?
