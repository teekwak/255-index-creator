import os
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


# print words to pages that word occurs on
with open('words_intermediate.tsv', 'w') as words_output_file:
  for key, value in pTokenizer.all_words.items():
    words_output_file.write('\n' + str(key) + '\t' + str(value))


# run page rank
pIterator = PageRankIterator(pTokenizer)
pIterator.initialize_page_rank()


# run 10 iterations of page rank
for i in range(1, 51):
  pIterator.temp_pages = pIterator.pages

  for id in pIterator.pages.keys():
    pIterator.temp_pages[id] = pIterator.calculate_page_rank(id)

  pIterator.pages = pIterator.temp_pages
  print('\rFinished ' + str(i) + ' iterations of PageRank', end='')


# print ranks to file
with open('pageranks_intermediate.tsv', 'w') as output_file:
  for key, value in pIterator.pages.items():
    output_file.write('\n' + str(key) + '\t' + str(value))


# upload sorted page ranks to redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
redis_counter = 0
for key, value in pTokenizer.all_words.items():
  sorted_pages = []
  for id in value:
    sorted_pages.append((id, pIterator.pages[id]))

  sorted_pages = sorted(sorted_pages, key=lambda x: x[1], reverse=True)
  r.rpush(key, *sorted_pages)
  redis_counter += 1
  print('\rUploaded ' + str(redis_counter) + ' words to Redis', end='')


# upload bookkeeping to redis
redis_counter = 0
for key, value in pTokenizer.bookkeeping.items():
  r.rpush('&_' + key, value)
  redis_counter += 1
  print('\rUploaded ' + str(redis_counter) + ' ids to Redis', end='')

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

