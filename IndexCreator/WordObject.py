class WordObject:
    def __init__(self, word):
        self.word = word
        self.pages = []

    def __hash__(self):
        return hash(str(self.word))

    def __eq__(self, other):
        return self.word == other.word
