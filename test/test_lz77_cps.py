import os
import unittest

from compression import lz77_cps
from generator import named, rand
from string_indexing import lpf

class TestLZ77CPS(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_round_trip(self, text, A = None):
    w = '#' + text
    stream, params, A, stats = lz77_cps.compress(w, len(text), A)
    self.assertEqual(lz77_cps.decompress(stream, len(text), params, A), w,
        f'Round trip failed for {text}')
    self.assertEqual(len(stream), stats.words * params.Lc,
        f'Stream is not a whole number of codewords for {text}')
    self.assertEqual(stats.source_symbols, len(text),
        f'Wrong number of source symbols counted for {text}')

  def check_factorization(self, text):
    w, n = '#' + text, len(text)
    _, LEN = lz77_cps.chen_puglisi_smyth_factorization(w, n)
    self.assertEqual(LEN, lpf.naive(w, n),
        f'CPS shows different then naive factorization for {text}')

  def test_cps_matches_naive(self):
    for text in ['a', 'ab', 'aaaaaaaa', 'aabbaabbbaaabbb', 'abasjdnaikjsdndwa']:
      self.check_factorization(text)

  def test_factors(self):
    factors = lz77_cps.factorize('#aabbaabba', 9)
    self.assertEqual([(f.len, f.literal) for f in factors],
                     [(0, 'a'), (1, 'b'), (1, 'a'), (3, 'a')])
    self.assertEqual([f.pos for f in factors], [1, 1, 3, 2])

  def test_parameters_max_len_0(self):
    _, params, _, _ = lz77_cps.compress('#1234', 4, ['1', '2', '3', '4'])
    self.assertEqual((params.n, params.max_len, params.Ll), (4, 0, 0))
    self.assertEqual(params.Lc, 1 + params.Lp)

  def test_round_trip_corners(self):
    self.check_round_trip('', ['a', 'b'])
    self.check_round_trip('a', ['a', 'b'])
    self.check_round_trip('ab')
    self.check_round_trip('aaaaaaaa', ['a', 'b'])
    self.check_round_trip('abbaabbbaaabab')
    self.check_round_trip('aacaacabcabaaac')
    self.check_round_trip('oasuieancojlasodiujdn')

  def test_round_trip_named_words(self):
    self.check_round_trip(named.fibonacci_word(10)[1:])
    self.check_round_trip(named.thue_word(6)[1:])

  @run_large
  def test_round_trip_named_words_large(self):
    self.check_round_trip(named.fibonacci_word(18)[1:])
    self.check_round_trip(named.thue_word(10)[1:])

  @run_large
  def test_round_trip_random(self):
    T, n = 10, 2000
    for A in [['0', '1'], ['a', 'b', 'c'], ['a', 'b', 'c', 'd']]:
      for _ in range(T):
        self.check_round_trip(rand.random_word(n, A)[1:], A)

if __name__ == '__main__':
  unittest.main()