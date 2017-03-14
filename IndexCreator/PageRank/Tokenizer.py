import bs4
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # requires python 3
from urllib.parse import urlparse

from IndexCreator.PageRank.Page import Page


class Tokenizer:
  def __init__(self, counter):
    self.total_number_of_files = counter
    self.bookkeeping = {}  # page -> id
    self.bookkeeping_urls = set()
    self.stop_words = []
    self.pageIncomingLinks = {}  # id -> set of ids pointing inwards
    # todo: list of pages objects?
    #       each page has the following properties:
    #         - number of outgoing links
    #         - a list of incoming link ids that are in our index
    self.all_pages = []  # list of page objects # todo: do i even need this? yes. you need to keep track of outgoing and incoming for each page
    self.all_words = {}  # word to set of pages? (will be accessed constantly, so dictionary is necessary)

    # we just need a SET of the words. we are using the words to find all documents that contain a word from the query
    # but then we just return the page with the highest page rank, which is independent of word count

  # todo: figure out what the end data structure looks like
  # todo: figure out what I need for data structure as the intermediate


  # puts bookkeeping.tsv to dictionary of id -> URL
  # sets id in pageIncomingLinkCount to 0
  def load_bookkeeping(self, filename):
    with open(filename) as file_object:
      for line in file_object:
        parts = line.strip().split("\t")
        self.bookkeeping[parts[0]] = parts[1]
        self.bookkeeping_urls.add(parts[1])
        self.pageIncomingLinks[parts[1]] = set()


  # stopwords from https://github.com/stanfordnlp/CoreNLP/blob/master/data/edu/stanford/nlp/patterns/surface/stopwords.txt
  # puts stopwords into list
  def load_stop_words(self, filename):
    with open(filename) as file_object:
      for line in file_object:
        self.stop_words.append(line.strip())


  # parses all words from a file by getting all the text, removing non-alphanumeric characters, splitting at space, and stripping
  def parse_file(self, filepath, id):
    page = Page(id)
    page.url = self.bookkeeping[id]

    soup = BeautifulSoup(file_to_string(filepath), 'html.parser')
    self.parse_anchor_tags(soup, page)
    self.parse_word_tokens(soup, page)
    self.all_pages.append(page)

    self.total_number_of_files -= 1
    # print('\rApproximate number of files left to parse: ' + str(self.total_number_of_files), end='')


  # parses words from a soup object and appends the set of sorted words to the page object
  def parse_word_tokens(self, soup, pageObject):
    text = soup.findAll(text=True)

    # remove invisible text, non-alphanumeric characters, and whitespace
    visible_text = []
    for text_element in remove_invisible_text(text):
      if len(text_element.strip()) > 0:
        text_element = remove_non_alphanumeric_characters(text_element)
        visible_text.extend([x.strip() for x in text_element.split() if len(x.strip()) > 0])

    # remove stopwords
    visible_text = set([x for x in visible_text if x not in self.stop_words])

    # add page's id to word dictionary
    for word in visible_text:
      if not word in self.all_words:
        self.all_words[word] = set()
      self.all_words[word].add(pageObject.id)


  # parses all anchor tags and checks if they exist in the pageIncomingLinkCount dictionary
  def parse_anchor_tags(self, soup, pageObject):
    outlinks = [urljoin('http://' + pageObject.url, tag['href']) for tag in soup.findAll('a') if tag.has_attr('href')]

    stripped_outlinks = [urlparse(x).netloc + urlparse(x).path for x in outlinks]

    pageObject.number_of_outgoing_links = len(stripped_outlinks)

    for link in stripped_outlinks:
      if link in self.bookkeeping_urls:
        self.pageIncomingLinks[pageObject.url].add(link)


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
