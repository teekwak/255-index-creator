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
        path_to_resources = 'resources/WEBPAGES_RAW'
        word_exp = '|'.join(words)

        s = "this is a machine learning algorithm for informationsecurity"

        print('x -> ' + str(re.findall(word_exp, s)))

        for foldername in os.listdir(path_to_resources):
            if os.path.isdir(path_to_resources + "/" + foldername):  # should exclude bookkeeping files
                for filename in os.listdir(path_to_resources + "/" + foldername):
                    if not filename.startswith("."):
                        with open(path_to_resources + "/" + foldername + "/" + filename, 'r') as fileobj:
                            filestr = fileobj.read()
                            found_words = re.findall(word_exp, filestr)
                            if len(found_words) > 0:
                                print(foldername + "/" + filename + " -> " + str(found_words))


if __name__ == '__main__':
    c = CorpusChecker()
    # c.check_content_type("resources/WEBPAGES_RAW/bookkeeping.tsv")
    # c.search_for_words(['machine', 'learning', 'information', 'retrieval', 'security', 'software', 'engineering', 'graduate', 'courses']);