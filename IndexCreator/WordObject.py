class WordObject:
    def __init__(self, word):
        self.word = word
        self.pages = []
        # self.title_occurrences = {}
        # self.header_occurrences = {}
        # self.body_occurrences = {}

    def __hash__(self):
        return hash(str(self.word))

    def __eq__(self, other):
        return self.word == other.word
