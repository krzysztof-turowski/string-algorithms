import unittest
from compression import lzw, lz78

COMPRESSION_ALGORITHMS = [
  (lzw.lzw_compress, lzw.lzw_decompress),
  (lz78.lz78_compress, lz78.lz78_decompress)
]

class TestCompressionWithOptimalParsing(unittest.TestCase):
  TEST_WORDS = [
    "abbbcaabbcbbcaaac",
    "abababaabaabaaab",
    "abccdeabccdeacdeacdeacde",
    "a",
    "",
    "ababcbababaa",
    "aaabbabaabaaabab",
    "abababcccacadcadaabcada"
  ]

  def get_alphabet(self, w):
    return sorted({c for c in w})

  def check_word(self, w):
    for (compressor, decompressor) in COMPRESSION_ALGORITHMS:
      compressed = compressor(w)
      decompressed = decompressor(compressed, self.get_alphabet(w))
      self.assertEqual(decompressed, w)

  def test_empty(self):
    self.check_word("")

  def test_one(self):
    self.check_word("a")

  def test_hand(self):
    for w in self.TEST_WORDS:
      self.check_word(w)

  