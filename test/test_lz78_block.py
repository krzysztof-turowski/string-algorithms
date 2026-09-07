import os
import unittest

from compression import lz78_block
from generator import named, rand

class TestLZ78Block(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_round_trip(self, text, block_length, A = None):
    w = '#' + text
    stream, params, A, stats = lz78_block.compress(
        w, len(text), block_length, A)
    self.assertEqual(
        lz78_block.decompress(stream, len(text), params, A), w,
        f'Round trip failed for {text} with n={block_length}')
    self.assertEqual(stats.source_symbols, len(text),
        f'Wrong number of source symbols counted for {text}')
    
  def check_all_parameters(self, text, A = None, large = False):
    block_lengths = [1024, 16] if large else [1, 4, 8]
    for block_length in block_lengths:
      self.check_round_trip(text, block_length, A)

  def test_codeword_width(self):
    params = lz78_block.make_params(2, 16)
    self.assertEqual(
        [lz78_block.codeword_width(params, j) for j in [1, 2, 3, 4, 5]],
        [1, 2, 3, 3, 4])
    params = lz78_block.make_params(3, 16)
    self.assertEqual(
        [lz78_block.codeword_width(params, j) for j in [1, 2, 3]], [2, 3, 4])

  def test_round_trip_corners(self):
    self.check_all_parameters('', ['a', 'b'])
    self.check_all_parameters('a', ['a', 'b'])
    self.check_all_parameters('ab')
    self.check_all_parameters('aaaaaaaa', ['a', 'b'])
    self.check_all_parameters('abbaabbbaaabab')
    self.check_all_parameters('aacaacabcabaaac')
    self.check_all_parameters('oasuieancojlasodiujdn')

  def test_round_trip_named_words(self):
    self.check_all_parameters(named.fibonacci_word(10)[1:])
    self.check_all_parameters(named.thue_word(6)[1:])

  @run_large
  def test_round_trip_named_words_large(self):
    self.check_all_parameters(named.fibonacci_word(18)[1:], large = True)
    self.check_all_parameters(named.thue_word(10)[1:], large = True)

  @run_large
  def test_round_trip_random(self):
    T, n = 10, 2000
    for A in [['0', '1'], ['a', 'b', 'c'], ['a', 'b', 'c', 'd']]:
      for _ in range(T):
        self.check_round_trip(rand.random_word(n, A)[1:], 1024, A)

if __name__ == '__main__':
  unittest.main()