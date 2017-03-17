import os

import math
import redis

from IndexCreator.PageRank.PageRankIterator import PageRankIterator
from IndexCreator.PageRank.Tokenizer import Tokenizer


path_to_resources = '../resources/WEBPAGES_RAW'

# get number of files
counter = 0
for foldername in os.listdir(path_to_resources):
  if os.path.isdir(path_to_resources + "/" + foldername):
      for filename in os.listdir(path_to_resources + "/" + foldername):
        if not filename.startswith("."):
          counter += 1


# parse files
pTokenizer = Tokenizer(counter)
pTokenizer.load_stop_words('../resources/stopwords.txt')
pTokenizer.load_bookkeeping('../resources/WEBPAGES_RAW/bookkeeping_queryless.tsv')

for foldername in os.listdir(path_to_resources):
  if os.path.isdir(path_to_resources + "/" + foldername):
    for filename in os.listdir(path_to_resources + "/" + foldername):
      if not filename.startswith("."):
        pTokenizer.parse_file(path_to_resources + "/" + foldername + "/" + filename, foldername + "/" + filename)


# append pages with no outgoing links to all other pages
for id in pTokenizer.pageIncomingLinks.keys():
  if not id in pTokenizer.pagesWithoutOutgoingLinks:
    pTokenizer.pageIncomingLinks[id].update(pTokenizer.pagesWithoutOutgoingLinks)


# update number of outlinks with no outgoing links
for id, outgoingLinksCount in pTokenizer.pageToOutgoingLinksCount.items():
  if outgoingLinksCount == 0:
    pTokenizer.pageToOutgoingLinksCount[id] = pTokenizer.number_of_files_parsed


# print words to pages that word occurs on
# with open('words_intermediate.tsv', 'w') as words_output_file:
#   for key, value in pTokenizer.all_words.items():
#     words_output_file.write('\n' + str(key) + '\t' + str(value))


# run page rank
pIterator = PageRankIterator(pTokenizer)
pIterator.initialize_page_rank()


# run 5 iterations of page rank (log(N), where N = size of index)
for i in range(1, 6):
  pIterator.temp_pages = pIterator.pages

  for id in pIterator.pages.keys():
    pIterator.temp_pages[id] = pIterator.calculate_page_rank(id)

  pIterator.pages = pIterator.temp_pages
  print('\rFinished ' + str(i) + ' iterations of PageRank', end='')


# print ranks to file
# with open('pageranks_intermediate.tsv', 'w') as output_file:
#   for key, value in pIterator.pages.items():
#     output_file.write('\n' + str(key) + '\t' + str(value))


# upload to redis: word -> list of page ids with word on them
redis_counter = 0
r = redis.StrictRedis(host='localhost', port=6379, db=0)
for key, value in pTokenizer.all_words.items():
  sorted_value = sorted(value)
  r.rpush(key, *sorted_value)
  redis_counter += 1
  print('\rUploaded ' + str(redis_counter) + ' words to Redis', end='')


# upload to redis: &wc_[id]_[word] -> number of times a word appears on a page
redis_counter = 0
for page_id, words in pTokenizer.page_word_frequencies.items():
  magnitude = 0.0
  for word, count in words.items():
    r.set('&wc_' + page_id + '_' + word, count)
    magnitude += (count * count)
    redis_counter += 1
    print('\rUploaded ' + str(redis_counter) + ' word occurrences to Redis', end='')
  r.set('&mag_' + page_id, math.sqrt(magnitude))


# upload to redis: &pr_[id] -> page rank score
redis_counter = 0
for key, value in pIterator.pages.items():
  r.set('&pr_' + key, value)
  redis_counter += 1
  print('\rUploaded ' + str(redis_counter) + ' page rank scores to Redis', end='')


# upload to redis: &id_[id] -> url
redis_counter = 0
with open('../resources/WEBPAGES_RAW/bookkeeping.tsv') as actual_bookkeeping_file:
  for line in actual_bookkeeping_file:
    parts = line.strip().split("\t")
    r.set('&id_' + parts[0], parts[1])
    redis_counter += 1
    print('\rUploaded ' + str(redis_counter) + ' ids to Redis', end='')


# complete
print('\n\nProcess completed successfully.')




# create normalized bookkeeping
#
# from urllib.parse import urlparse
# new_file_lines = []
# with open('../resources/WEBPAGES_RAW/bookkeeping.tsv') as file_object:
#   for line in file_object:
#     line_parts = line.strip().split('\t')
#     parse_results = urlparse(line_parts[1])
#     new_file_lines.append(line_parts[0] + '\t' + parse_results.netloc + parse_results.path)
#
#
# with open('../resources/WEBPAGES_RAW/bookkeeping_queryless.tsv', 'w') as new_file:
#   new_file.write('\n'.join(new_file_lines))

