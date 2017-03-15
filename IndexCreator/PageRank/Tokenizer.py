import bs4
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # requires python 3
from urllib.parse import urlparse
from stemming.porter2 import stem


class Tokenizer:
  def __init__(self, counter):
    self.number_of_files_parsed = 0
    self.total_number_of_files = counter
    self.bookkeeping = {}  # id -> page
    self.reverse_bookkeeping = {} # page -> id
    self.stop_words = []
    self.pageIncomingLinks = {}  # id -> set of ids pointing inwards
    self.pageToOutgoingLinksCount = {}  # id -> number of outlinks
    self.all_words = {}  # word to set of pages? (will be accessed constantly, so dictionary is necessary)

  # todo: figure out what the end data structure looks like
  # todo: figure out what I need for data structure as the intermediate


  # puts bookkeeping.tsv to dictionary of id -> URL
  # sets id in pageIncomingLinkCount to 0
  def load_bookkeeping(self, filename):
    with open(filename) as file_object:
      for line in file_object:
        parts = line.strip().split("\t")
        self.bookkeeping[parts[0]] = parts[1]
        self.reverse_bookkeeping[parts[1]] = parts[0]
        self.pageIncomingLinks[parts[0]] = set()


  # stopwords from https://github.com/stanfordnlp/CoreNLP/blob/master/data/edu/stanford/nlp/patterns/surface/stopwords.txt
  # puts stopwords into list
  def load_stop_words(self, filename):
    with open(filename) as file_object:
      for line in file_object:
        self.stop_words.append(line.strip())


  # parses all words from a file by getting all the text, removing non-alphanumeric characters, splitting at space, and stripping
  def parse_file(self, filepath, id):
    soup = BeautifulSoup(file_to_string(filepath), 'html.parser')
    self.pageToOutgoingLinksCount[id] = self.parse_anchor_tags(soup, id, self.bookkeeping[id])
    self.parse_word_tokens(soup, id)
    self.number_of_files_parsed += 1
    print('\rApproximate number of files left to parse: ' + str(self.number_of_files_parsed) + '/' + str(self.total_number_of_files), end='')


  # parses all anchor tags and checks if they exist in the pageIncomingLinkCount dictionary
  def parse_anchor_tags(self, soup, id, url):
    outlinks = [urljoin('http://' + url, tag['href']) for tag in soup.findAll('a') if tag.has_attr('href')]

    stripped_outlinks = [urlparse(x).netloc + urlparse(x).path for x in outlinks]

    for link in stripped_outlinks:
      if link in self.reverse_bookkeeping:
        self.pageIncomingLinks[id].add(self.reverse_bookkeeping[link])

    return len(stripped_outlinks)


  # parses words from a soup object and appends the set of sorted words to the page object
  def parse_word_tokens(self, soup, id):
    text = soup.findAll(text=True)

    # remove invisible text, non-alphanumeric characters, and whitespace
    visible_text = []
    for text_element in remove_invisible_text(text):
      if len(text_element.strip()) > 0:
        text_element = remove_non_alphanumeric_characters(text_element)
        visible_text.extend([x.strip() for x in text_element.split() if len(x.strip()) > 0])

    # remove stopwords
    visible_text = set([stem(x) for x in visible_text if x not in self.stop_words])

    # add page's id to word dictionary
    for word in visible_text:
      if not word in self.all_words:
        self.all_words[word] = set()
      self.all_words[word].add(id)


# returns file as string. replaces <br/> tags with newline character
def file_to_string(filepath):
  with open(filepath, 'r') as fileobject:
    return re.sub(r'<br\W*>', '\n', str.lower(fileobject.read()))


# removes non-alphanumeric characters from a string
def remove_non_alphanumeric_characters(word):
  return re.sub(r'[^\w_]|_', ' ', word)


# removes invisible text
def remove_invisible_text(text):
  return [x for x in list(filter(visible, text))]


# modification from http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
# removes text found in style tags, scrip tags, and document tags (e.g. DOCTYPE)
def visible(element):
  if element.parent.name in ['style', 'script', '[document]']:
    return False
  elif isinstance(element, bs4.element.Comment):
    return False
  return True
