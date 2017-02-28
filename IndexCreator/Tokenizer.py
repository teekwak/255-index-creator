import bs4
from bs4 import BeautifulSoup # the library to parse things
import os
import string
import re
import sys

class Tokenizer:
    def __init__(self):
        self.path_to_resources = 'resources/WEBPAGES_RAW/'
        self.current_page_contents = ''
        self.soup = None
        self.title_tokens = {}
        self.header_tokens = {}
        self.body_tokens = {}
        self.stop_words = []


    # from https://github.com/stanfordnlp/CoreNLP/blob/master/data/edu/stanford/nlp/patterns/surface/stopwords.txt
    def load_stop_words(self, filename):
        with open(filename) as file_object:
            for line in file_object:
                self.stop_words.append(line.strip())


    def get_title_tokens(self):
        title_text = str(self.soup.title.string).strip()
        title_text = remove_ascii_punctuation(title_text)

        self.title_tokens = {}

        for key in [x.strip() for x in title_text.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words]:
            if key in self.title_tokens:
                self.title_tokens[key] += 1
            else:
                self.title_tokens[key] = 1


    def get_header_tokens(self):
        header_text = []
        for tag in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            header_text.append(remove_ascii_punctuation(tag.text))

        header_tokens = []
        for phrase in header_text:
            header_tokens.extend([x.strip() for x in phrase.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words])


        for key in header_tokens:
            if key in self.header_tokens:
                self.header_tokens[key] += 1
            else:
                self.header_tokens[key] = 1


    def get_body_tokens(self):
        text = self.soup.findAll(text=True)

        visible_text = remove_invisible_text(text)

        for i in range(len(visible_text)):
            visible_text[i] = remove_ascii_punctuation(visible_text[i])

        # split at space and remove string literals?
        body_tokens = []
        for phrase in visible_text:
            body_tokens.extend([x.strip() for x in phrase.split(' ') if len(x.strip()) > 0 and x.strip() not in self.stop_words])

        for key in body_tokens:
            if key in self.body_tokens:
                self.body_tokens[key] += 1
            else:
                self.body_tokens[key] = 1

        self.body_tokens = self.remove_header_token_duplicates(self.body_tokens)


    def get_files(self):
        for foldername in os.listdir(self.path_to_resources):
            if os.path.isdir(self.path_to_resources + foldername):

                if foldername == '0':
                    for filename in os.listdir(self.path_to_resources + foldername):
                        if(filename == '9'):
                            self.read_file_contents(self.path_to_resources + foldername + "/" + filename)
                            self.soup = BeautifulSoup(self.current_page_contents, 'html.parser')

                            self.get_title_tokens()
                            self.get_header_tokens()
                            self.get_body_tokens()


    def read_file_contents(self, filepath):
        with open(filepath, 'r') as fileobject:
            self.current_page_contents = str.lower(fileobject.read())

            # todo: clean unclosed tags using the prettify function (see file 0-1)
            # todo: rewrite those files to a new resources directory?
            # todo: what to do about file 0-0 (the one with only numbers?
            # todo: make another class just to parse text (INCLUDES header tags, list tags, paragraph tags, etc)
            # todo: remove apostrophe s
            # todo: stemming? remove contractions


    def remove_header_token_duplicates(self, dictionary):
        temp_dict = dictionary

        # remove header text to stop double counting
        for word in self.header_tokens:
            temp_dict[word] -= 1

        to_delete = []
        for word in temp_dict:
            if temp_dict[word] == 0:
                to_delete.append(word)

        for w in to_delete:
            temp_dict.pop(w, None)

        return temp_dict


'''
Removes ASCII punctuation from a string (not a list)
'''
def remove_ascii_punctuation(word):
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    return word.translate(translator).strip()


# modification from http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def remove_invisible_text(text):
    return [x for x in list(filter(visible, text))]


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif isinstance(element, bs4.element.Comment):
        return False
    return True


if __name__ == '__main__':
    t = Tokenizer()
    t.load_stop_words('stopwords.txt')
    t.get_files()
    print(t.body_tokens)