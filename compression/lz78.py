from compression.core import compressor, parser
from compression.core.dictionary import TrieReverseTrie

class LZ78DictParser(parser.DictParser):
  def __init__(self, dictionary):
    super().__init__(
      dictionary, 
      lambda dict_parser, c: (dict_parser.phrase.index, c, dict_parser.dict.size + 1),
      lambda dict_parser, c: dict_parser.dict.T
    ) 

class LZ78Compressor(compressor.Compressor):
  def __init__(self, alphabet):
    dictionary = TrieReverseTrie()
    super().__init__(
      dictionary, 
      LZ78DictParser,
      parser.OptimalOutputParser
    )  

class LZ78Decompressor(compressor.Decompressor):
  def __init__(self, alphabet):
    dictionary = TrieReverseTrie()
    super().__init__(dictionary, LZ78DictParser)
    
    self.reference[0] = dictionary.T

  def parse(self, d):
    c = d[0]
    if c in self.reference:
      print('mam kod', c)
      node = self.reference[c]
      tmp = d[1]
      while node.parent != node:
        tmp += node.edge
        node = node.parent
      tmp = tmp[::-1]
      for x in tmp:
        print('parse', x)
        added = self.parser_dictionary.parse(x)
        if added is not None:
          print('added', added.index)
          self.reference[added.index] = added
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
