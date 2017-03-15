import requests
import os
import re


class CorpusChecker:
    def __init__(self):
        self.invalid_urls = []

    def check_content_type(self, filename):
        with open(filename) as fileobj:

            count = 0

            for line in fileobj:
                try:
                    parts = line.split("\t")
                    r = requests.get("http://" + parts[1], timeout=3)

                    if not str(r.headers['content-type']).startswith("text/html"):
                        self.invalid_urls.append(parts[0])

                    count += 1
                    print("\rProcessed " + str(count) + " files", end='')
                except Exception as e:
                    pass

            for x in self.invalid_urls:
                print(x)

    def search_for_words(self, words):
        path_to_resources = '../resources/WEBPAGES_RAW'
        word_exp = '|'.join(words)

        for foldername in os.listdir(path_to_resources):
            if os.path.isdir(path_to_resources + "/" + foldername):  # should exclude bookkeeping files
                for filename in os.listdir(path_to_resources + "/" + foldername):
                    if not filename.startswith("."):
                        with open(path_to_resources + "/" + foldername + "/" + filename, 'r') as fileobj:
                            filestr = fileobj.read()
                            found_words = re.findall(word_exp, filestr)
                            if len(found_words) > 0:
                                print(foldername + "/" + filename + " -> " + str(found_words))


    def search_for_url(self, urls):
      path_to_resources = '../resources/WEBPAGES_RAW'

      bookkeeping = set()
      with open(path_to_resources + "/bookkeeping.tsv") as bookkeeping_file:
        for line in bookkeeping_file:
          parsed = line.strip().split("\t")
          bookkeeping.add(parsed[1])

      with open(path_to_resources + '/bookkeeping_queryless.tsv') as queryless_bookkeeping_file:
        for line in queryless_bookkeeping_file:
          parsed = line.strip().split("\t")
          bookkeeping.add(parsed[1])

      for url in urls:
        isFound = url in bookkeeping
        print(str(url) + " -> " + str(isFound))


if __name__ == '__main__':
    c = CorpusChecker()
    # c.check_content_type("resources/WEBPAGES_RAW/bookkeeping.tsv")
    # c.search_for_words(['machine', 'learning', 'information', 'retrieval', 'security', 'software', 'engineering', 'graduate', 'courses']);
    # c.search_for_words(["https://grape/svn/group/codebase/appstring/tags/release-1.0/"])
    c.search_for_url([
      'www.ics.uci.edu/~lopes/teaching/cs221W15/',
      'www.ics.uci.edu/~djp3/classes/2009_01_02_INF141/calendar.html',
      'www.ics.uci.edu/~lopes/teaching/cs221W13/',
      'www.ics.uci.edu/~djp3/classes/2014_01_INF141/calendar.html',
      'www.ics.uci.edu/~djp3/classes/2010_01_CS221/'
    ])
