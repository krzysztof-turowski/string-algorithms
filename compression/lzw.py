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
    code = self.parser_output.parse(c)
    self.parser_dictionary.parse(c)
    return code

class LZWDecompressor(compressor.Decompressor):
  def __init__(self, alphabet):
    dictionary = TrieReverseTrie()
    super().__init__(dictionary, LZWDictParser)

    for i in range(len(alphabet)):
      self.reference[i] = dictionary.insert(dictionary.T, alphabet[i], alphabet[i], i)
      
  def parse(self, c):
    node = None
    if c in self.reference:
      node = self.reference[c]
    else:
      node = self.parser_dictionary.phrase

    prefix = self.parser_dictionary.dict.get_prefix(node)
    for x in prefix:
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
    node = self.reference[c]

    phrase = self.parser_dictionary.dict.get_prefix(node)
    for x in phrase[len(prefix):]:
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
    return phrase

def get_alphabet(w):
  return sorted({c for c in w})

def lzw_compress(w):
  alphabet = get_alphabet(w)
  instance = LZWCompressor(alphabet)
  compressed = []
  for c in w:
    code = instance.parse(c)
    if code:
      compressed.append(code)
  code = instance.finish()
  if code is not None:
    compressed += code
  return compressed

def lzw_decompress(code, alphabet):
  instance = LZWDecompressor(alphabet)
  decompressed = ""
  for c in code:
    c = int(c)
    decompressed += instance.parse(c)
  return decompressed
