import os
import unittest

from compression import lz77_sliding_window
from generator import named, rand

class TestLZ77SlidingWindow(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_round_trip(self, text, buffer_length, lookahead_length, A = None):
    w = '#' + text
    stream, params, A, stats = lz77_sliding_window.compress(
        w, len(text), buffer_length, lookahead_length, A)
    self.assertEqual(
        lz77_sliding_window.decompress(stream, len(text), params, A), w,
        f'Round trip failed for {text} with n={buffer_length}, '
        f'Ls={lookahead_length}')
    self.assertEqual(len(stream), stats.words * params.Lc,
        f'Stream is not a whole number of codewords for {text}')
    self.assertEqual(stats.source_symbols, len(text),
        f'Wrong number of source symbols counted for {text}')

  def check_all_parameters(self, text, A = None, large = False):
    parameters = [(1024, 16)] if large else [
        (2 * lookahead_length, lookahead_length)
        for lookahead_length in [2, 4, 8]]
    for buffer_length, lookahead_length in parameters:
      self.check_round_trip(text, buffer_length, lookahead_length, A)

  def test_parameters(self):
    params = lz77_sliding_window.make_params(2, 16, 4)
    self.assertEqual((params.Lp, params.Ll, params.Lc), (4, 2, 7))
    self.assertEqual(params.window_size, 12)

    params = lz77_sliding_window.make_params(3, 27, 9)
    self.assertEqual((params.Lp, params.Ll, params.Lc), (3, 2, 6))

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
        self.check_round_trip(rand.random_word(n, A)[1:], 1024, 32, A)

if __name__ == '__main__':
  unittest.main()