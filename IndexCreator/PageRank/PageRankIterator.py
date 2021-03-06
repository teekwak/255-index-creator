class PageRankIterator:
  def __init__(self, tokenizerObject):
    self.tokenizer = tokenizerObject
    self.DAMPENING_FACTOR = 0.85  # from literature
    self.pages = {}

  # set page rank of all pages to 1 / N
  def initialize_page_rank(self):
    for id in self.tokenizer.bookkeeping.keys():
      self.pages[id] = 1 / self.tokenizer.number_of_files_parsed

  # calculate page rank
  def calculate_page_rank(self, pageId):
    # calculate sum of all incoming pages's page ranks
    sumOfIncomingPageRanks = 0

    for id in self.tokenizer.pageIncomingLinks[pageId]:
      if id in self.tokenizer.pageToOutgoingLinksCount: # todo: just for test purposes. links will not all exist during testing
        if self.tokenizer.pageToOutgoingLinksCount[id] != 0:
          sumOfIncomingPageRanks += (self.pages[id] / self.tokenizer.pageToOutgoingLinksCount[id])

    # return page rank formula: PR(A) = (1 - d) / N + d * sum(PR(i)/len(outgoing(i))) for each incoming i
    return ((1 - self.DAMPENING_FACTOR) / self.tokenizer.number_of_files_parsed) + (self.DAMPENING_FACTOR * sumOfIncomingPageRanks)
