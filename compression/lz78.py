from compression.core import compressor, parser
from compression.core.dictionary import TrieReverseTrie
from ast import literal_eval as make_tuple

class LZ78DictParser(parser.DictParser):
  def __init__(self, dictionary):
    super().__init__(
      dictionary, 
      lambda dict_parser, c: (dict_parser.phrase.index, c),
      lambda dict_parser, c: dict_parser.dict.T
    ) 

class LZ78Compressor(compressor.Compressor):
  def __init__(self):
    dictionary = TrieReverseTrie()
    super().__init__(
      dictionary, 
      LZ78DictParser,
      parser.OptimalOutputParser
    )  

class LZ78Decompressor(compressor.Decompressor):
  def __init__(self):
    dictionary = TrieReverseTrie()
    super().__init__(dictionary, LZ78DictParser)
    
    self.reference[0] = dictionary.T

  def parse(self, c):
    node = self.reference[c[0]]
    phrase = self.parser_dictionary.dict.get_prefix(node) + c[1]
    for x in phrase:
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.index] = added
    return phrase

def lz78_compress(w):
  instance = LZ78Compressor()
  compressed = []
  for c in w:
    code = instance.parse(c)
    if code:
      compressed.append(code)
  code = instance.finish()
  if code:
    compressed += code
  return compressed

def lz78_decompress(code, alphabet):
  instance = LZ78Decompressor()
  decompressed = ""
  for c in code:
    c = make_tuple(c)
    decompressed += instance.parse(c)
  return decompressed
