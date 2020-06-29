from compression.core import compressor, parser
from compression.core.dictionary import TrieReverseTrie

class LZWDictParser(parser.DictParser):
  def __init__(self, dictionary):
    super().__init__(
      dictionary, 
      lambda dict_parser, c: dict_parser.dict.size,
      lambda dict_parser, c: dict_parser.dict.T.search(c)
    )

class LZWCompressor(compressor.Compressor):
  def __init__(self, alphabet):
    dictionary = TrieReverseTrie()
    super().__init__(
      dictionary, 
      LZWDictParser,
      parser.OptimalOutputParser
    )

    for i in range(len(alphabet)):
      dictionary.insert(dictionary.T, alphabet[i], alphabet[i], i)

  def parse(self, c):
    self.parser_output.parse(c)
    self.parser_dictionary.parse(c)

class LZWDecompressor(compressor.Decompressor):
  def __init__(self, alphabet):
    dictionary = TrieReverseTrie()
    super().__init__(dictionary, LZWDictParser)

    for i in range(len(alphabet)):
      self.reference[i] = dictionary.insert(dictionary.T, alphabet[i], alphabet[i], i)
      
  def parse(self, c):
    c = int(c)
    if c in self.reference:
      print('mam kod', c)
      node = self.reference[c]
      tmp = ""
      while node.parent != node:
        tmp += node.edge
        node = node.parent
      tmp = tmp[::-1]
      for x in tmp:
        print('parse', x)
        added = self.parser_dictionary.parse(x)
        if added is not None:
          self.reference[added.label] = added
      return tmp
    # else self.reference[c] is None
    print('nie mam jeszcze kodu', c)
    node = self.parser_dictionary.phrase
    tmp = ""
    while node.parent != node:
      tmp += node.edge
      node = node.parent
    tmp = tmp[::-1]
    tmp2 = tmp
    ans = ""
    for x in tmp:
      print('parse', x)
      tmp2 += x
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
        if added.label == c:
          ans = tmp2
        # break
        # break or not to break?
    for x in ans[len(tmp):]:
      print('parse', x)
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
    print('a teraz juz mam?', c in self.reference)
    return ans
