import os
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
    if foldername in ['0', '1']: # todo: remove this line after testing
      for filename in os.listdir(path_to_resources + "/" + foldername):
        if not filename.startswith("."):
          pTokenizer.parse_file(path_to_resources + "/" + foldername + "/" + filename, foldername + "/" + filename)



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

