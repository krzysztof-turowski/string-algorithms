from compression.core import compressor, parser
from compression.core.dictionary import TrieReverseTrie

# pylint: disable=too-few-public-methods
class LZWDictParser(parser.DictParser):
  def __init__(self, dictionary):
    super(LZWDictParser, self).__init__(
        dictionary,
        lambda dict_parser, c: dict_parser.dict.size,
        lambda dict_parser, c: dict_parser.dict.trie.search(c)
    )

class LZWCompressor(compressor.Compressor):
  def __init__(self, parser_output, alphabet):
    dictionary = TrieReverseTrie()
    super(LZWCompressor, self).__init__(
        dictionary,
        LZWDictParser,
        parser_output
    )

    for k, v in enumerate(alphabet):
      dictionary.insert(dictionary.trie, v, v, k)

  def parse(self, c):
    code = self.parser_output.parse(c)
    self.parser_dictionary.parse(c)
    return code

# pylint: disable=too-few-public-methods
class LZWDecompressor(compressor.Decompressor):
  def __init__(self, alphabet):
    dictionary = TrieReverseTrie()
    super(LZWDecompressor, self).__init__(dictionary, LZWDictParser)

    for k, v in enumerate(alphabet):
      self.reference[k] = dictionary.insert(dictionary.trie, v, v, k)

  def parse(self, c):
    node = None
    parsed = ""

    while c not in self.reference:
      node = self.parser_dictionary.phrase
      prefix = self.parser_dictionary.dict.get_prefix(node)

      for x in prefix:
        parsed += x
        added = self.parser_dictionary.parse(x)
        if added is not None:
          self.reference[added.label] = added
          if added.label == c:
            break

    node = self.reference[c]
    phrase = self.parser_dictionary.dict.get_prefix(node)

    for x in phrase[len(parsed):]:
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added

    return phrase

def get_alphabet(w):
  return sorted({c for c in w})

def lzw_compress(w, parser_output=parser.OptimalOutputParser):
  alphabet = get_alphabet(w)
  instance = LZWCompressor(parser_output, alphabet)
  compressed = []
  for c in w[1:]:
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
