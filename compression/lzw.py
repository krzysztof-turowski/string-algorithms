from compression.core import parser
from compression.core.dictionary import SimpleDict, TrieDict

class LZW:

  def __init__(self, alphabet):
    self.dictionary = TrieDict('$')
    self.parser_dictionary = parser.LZWTrieDictParser(
        self.dictionary, len(alphabet)
    )
    self.parser_output = parser.GreedyOutputParser(self.dictionary)

    print(alphabet)
    for i in range(len(alphabet)):
      self.dictionary.insert(alphabet[i], i)
    print(self.dictionary.children)
    self.it = 1

  def parse(self, c):
    print("{2} ({0}): {1}".format(c, self.parser_output.parse(c), self.it))
    print("{2} ({0}): {1}".format(c, self.parser_dictionary.parse(c), self.it))
    self.it += 1

  def finish(self):
    print(self.parser_output.parse(''))
    return self.parser_output.output
