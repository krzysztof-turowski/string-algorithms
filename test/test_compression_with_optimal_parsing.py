import os
import unittest
from compression import lzw, lz78
from compression.core import parser
from generator.rand import random_word

COMPRESSION_ALGORITHMS = [
    (lzw.lzw_compress, lzw.lzw_decompress),
    (lz78.lz78_compress, lz78.lz78_decompress)
]

def get_alphabet(w):
  return sorted({c for c in w})

class TestCompressionWithOptimalParsing(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  TEST_WORDS = [
      '#',
      '#a',
      '#aaabbabaabaaabab',
      '#abababaabaabaaab',
      '#abababcccacadcadaabcada',
      '#ababcbababaa',
      '#abbbcaabbcbbcaaac',
      '#abccdeabccdeacdeacdeacde',
      '#bcbbbacbba',
      '#bbbbb'
  ]

  TEST_WORDS_LZW_OPTIMAL = [
      '#abababaabaabaaab'
  ]

  TEST_WORDS_LZ78_OPTIMAL = [
      '#abababcccacadcadaabcada'
  ]

  def check_word(self, w):
    for (compressor, decompressor) in COMPRESSION_ALGORITHMS:
      compressed = compressor(w)
      decompressed = decompressor(compressed, get_alphabet(w))
      self.assertEqual(decompressed, w[1:])

      compressed_greedy = compressor(w, parser.GreedyOutputParser)
      decompressed_greedy = decompressor(compressed, get_alphabet(w))
      self.assertEqual(decompressed_greedy, w[1:])

      self.assertLessEqual(len(compressed), len(compressed_greedy))

  def test_empty(self):
    self.check_word("#")

  def test_one_letter(self):
    self.check_word("#a")

  def test_hand(self):
    for w in self.TEST_WORDS:
      self.check_word(w)

  def test_lzw_optimality(self):
    for w in self.TEST_WORDS_LZW_OPTIMAL:
      compressed = lzw.lzw_compress(w)
      compressed_greedy = lzw.lzw_compress(w, parser.GreedyOutputParser)

      self.assertLess(len(compressed), len(compressed_greedy))

  def test_lz78_optimality(self):
    for w in self.TEST_WORDS_LZ78_OPTIMAL:
      compressed = lz78.lz78_compress(w)
      compressed_greedy = lz78.lz78_compress(w, parser.GreedyOutputParser)

      self.assertLess(len(compressed), len(compressed_greedy))

  @run_large
  def test_large_random(self):
    m, A = 10, ['a', 'b', 'c']
    for _ in range(1000):
      w = random_word(m, A)
      self.check_word(w)
