import bs4
from bs4 import BeautifulSoup # the library to parse things
import os
import string
import re

class FileCleaner:
    def __init__(self):
        self.path_to_resources = 'resources/WEBPAGES_RAW/'
        self.current_page_contents = ''

    def get_files(self):
        for foldername in os.listdir(self.path_to_resources):
            if os.path.isdir(self.path_to_resources + foldername):

                if foldername == '0':
                    for filename in os.listdir(self.path_to_resources + foldername):
                        if(filename == '4'):
                            self.read_file_contents(self.path_to_resources + foldername + "/" + filename)
                            soup = BeautifulSoup(self.current_page_contents, 'html.parser')
                            text = soup.findAll(text=True)

                            # filter out invisible text
                            visible_text = [x for x in list(filter(self.visible, text))]

                            # remove ascii punctuation
                            translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
                            visible_text = [x.translate(translator) for x in visible_text if len(x.strip()) > 0]

                            # split at space and remove string literals?
                            all_words = []
                            for phrase in visible_text:
                                all_words.extend([x.strip() for x in phrase.split(' ') if len(x.strip()) > 0])

                            # put words into dictionary
                            words = {}
                            for word in all_words:
                                if word in words:
                                    words[word] += 1
                                else:
                                    words[word] = 1

                            for key, value in words.items():
                                print(key + " -> " + str(value))

    def visible(self, element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif isinstance(element, bs4.element.Comment):
            return False
        return True


    def read_file_contents(self, filepath):
        with open(filepath, 'r') as fileobject:
            self.current_page_contents = str.lower(fileobject.read())

            # todo: clean unclosed tags using the prettify function (see file 0-1)
            # todo: rewrite those files to a new resources directory?
            # todo: what to do about file 0-0 (the one with only numbers?
            # todo: make another class just to parse text (INCLUDES header tags, list tags, paragraph tags, etc)

if __name__ == '__main__':
    f = FileCleaner()
    f.get_files()