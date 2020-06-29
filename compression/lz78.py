from ast import literal_eval as make_tuple
from compression.core import compressor, parser
from compression.core.dictionary import TrieReverseTrie

# pylint: disable=too-few-public-methods
class LZ78DictParser(parser.DictParser):
  def __init__(self, dictionary):
    super(LZ78DictParser, self).__init__(
        dictionary,
        lambda dict_parser, c: (dict_parser.phrase.index, c),
        lambda dict_parser, c: dict_parser.dict.trie
    )

class LZ78Compressor(compressor.Compressor):
  def __init__(self, parser_output):
    dictionary = TrieReverseTrie()
    super(LZ78Compressor, self).__init__(
        dictionary,
        LZ78DictParser,
        parser_output
    )

# pylint: disable=too-few-public-methods
class LZ78Decompressor(compressor.Decompressor):
  def __init__(self):
    dictionary = TrieReverseTrie()
    super(LZ78Decompressor, self).__init__(dictionary, LZ78DictParser)

    self.reference[0] = dictionary.trie

  def parse(self, c):
    node = self.reference[c[0]]
    phrase = self.parser_dictionary.dict.get_prefix(node) + c[1]
    for x in phrase:
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.index] = added
    return phrase

def lz78_compress(w, parser_output=parser.OptimalOutputParser):
  instance = LZ78Compressor(parser_output)
  compressed = []
  for c in w[1:]:
    code = instance.parse(c)
    if code:
      compressed.append(code)
  code = instance.finish()
  if code:
    compressed += code
  return compressed

# pylint: disable=unused-argument
def lz78_decompress(code, alphabet=None):
  instance = LZ78Decompressor()
  decompressed = ""
  for c in code:
    c = make_tuple(c)
    decompressed += instance.parse(c)
  return decompressed
