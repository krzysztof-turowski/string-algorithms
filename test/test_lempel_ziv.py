import itertools
import os
import unittest
import string

from compression import lempel_ziv, lz77_cps, lz77_sliding_window, lz78_block
from generator import rand, named

import parameterized

from string_indexing import lpf

def lz77_sliding_window_compress(w, n, A):
  return lz77_sliding_window.compress(w, n, 1024, 32, A)

def lz78_block_compress(w, n, A):
  return lz78_block.compress(w, n, 1024, A)

LEMPEL_ZIV_CODECS = [
  [
    'LZ77 sliding window',
    lz77_sliding_window_compress,
    lz77_sliding_window.decompress,
  ],
  [ 'LZ78 block', lz78_block_compress, lz78_block.decompress ],
  [
    'LZ77 with CPS factorization',
    lz77_cps.compress,
    lz77_cps.decompress
  ],
]

class TestLempelZiv77(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_factorization(self, text, reference, algorithm):
    self.assertEqual(algorithm('#' + text, len(text)), reference)

  def check_all_factorizations(self, text, reference=None):
    reference =  reference if reference is not None \
      else lempel_ziv.naive_factorization('#' + text, len(text))
    self.check_factorization(text, reference,
                             lempel_ziv.naive_factorization)
    self.check_factorization(text, reference,
                             lempel_ziv.crochemore_ilie_smyth)

  def test_lz_factorization_corners(self):
    # "Linear time Lempel-Ziv Factorization: Simple, Fast, Small", page 3
    self.check_all_factorizations(
        'zzzzzipzip',
        [(1, 0, 'z'), (2, 4, 'z'), (6, 0, 'i'), (7, 0, 'p'), (8, 3, 'z')])

    # "A simple algorithm for computing the Lempel-Ziv factorization", page 1
    self.check_all_factorizations(
        'abbaabbbaaabab',
        [(1, 0, 'a'), (2, 0, 'b'), (3, 1, 'b'), (4, 1, 'a'), (5, 3, 'a'),
         (8, 3, 'b'), (11, 2, 'a'), (13, 2, 'a')])

    self.check_all_factorizations('', [])
    self.check_all_factorizations('a', [(1, 0, 'a')])
    self.check_all_factorizations('aa', [(1, 0, 'a'), (2, 1, 'a')])
    self.check_all_factorizations('ab', [(1, 0, 'a'), (2, 0, 'b')])
    self.check_all_factorizations('aaaa', [(1, 0, 'a'), (2, 3, 'a')])
    self.check_all_factorizations('abab', [(1, 0, 'a'), (2, 0, 'b'),
                                           (3, 2, 'a')])
    self.check_all_factorizations('ababcbababaa')
    self.check_all_factorizations('eacacad')
    self.check_all_factorizations('aacaacabcabaaac')
    self.check_all_factorizations('abaab')
    self.check_all_factorizations('ababcbababaa')
    self.check_all_factorizations('aabbbbc')

  @run_large
  def test_lz_factorization_random(self):
    T, n, A = 100, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_all_factorizations(text)

  @run_large
  def test_lz_factorization_random_short_strings(self):
    T, n, A = 5, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_all_factorizations(text)

  @run_large
  def test_lz_factorization_random_cyclic(self):
    T, n, A = 10, 200, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      text = text * 10
      self.check_all_factorizations(text)

  @run_large
  def test_lz_factorization_random_big_alphabet(self):
    T, n, A = 100, 500, string.ascii_letters + string.digits
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_all_factorizations(text)

  def check_lempel_ziv_77(self, t, n, reference):
    self.assertEqual(lempel_ziv.lz77(t, n), reference)

  def check_recode_lempel_ziv_77(self, t, n):
    self.assertEqual(lempel_ziv.inverse_lz77(lempel_ziv.lz77(t, n)), t)

  def test_lempel_ziv_77(self):
    self.check_lempel_ziv_77(
        '#ababcbababaa', 12,
        [(0, 0, 'a'), (0, 0, 'b'), (2, 2, 'c'), (4, 3, 'a'), (2, 2, 'a')])
    self.check_lempel_ziv_77(
        '#aacaacabcabaaac', 15,
        [(0, 0, 'a'), (1, 1, 'c'), (3, 4, 'b'), (3, 3, 'a'), (1, 2, 'c')])

  def test_recode_lempel_ziv_77(self):
    self.check_recode_lempel_ziv_77('#ababcbababaa', 12)
    self.check_recode_lempel_ziv_77('#aacaacabcabaaac', 15)

  @run_large
  def test_random_recode_lempel_ziv_77(self):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      self.check_recode_lempel_ziv_77(t, n)

  @run_large
  def test_all_recode_lempel_ziv_77(self):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        self.check_recode_lempel_ziv_77(t, n)

  def test_lz77_sliding_window_parameters(self):
    parameters = lz77_sliding_window.make_parameters(2, 16, 4)
    self.assertEqual(
        (parameters.Lp, parameters.Ll, parameters.Lc), (4, 2, 7))
    self.assertEqual(parameters.window_size, 12)

    parameters = lz77_sliding_window.make_parameters(3, 27, 9)
    self.assertEqual(
        (parameters.Lp, parameters.Ll, parameters.Lc), (3, 2, 6))

  def test_lz78_block_codeword_width(self):
    parameters = lz78_block.make_parameters(2, 16)
    self.assertEqual(
        [lz78_block.codeword_width(parameters, j) for j in [1, 2, 3, 4, 5]],
        [1, 2, 3, 3, 4])
    parameters = lz78_block.make_parameters(3, 16)
    self.assertEqual(
        [lz78_block.codeword_width(parameters, j) for j in [1, 2, 3]],
        [2, 3, 4])

  def check_cps_factorization(self, text):
    w, n = '#' + text, len(text)
    _, LEN = lz77_cps.chen_puglisi_smyth_factorization(w, n)
    self.assertEqual(LEN, lpf.naive(w, n),
        f'CPS shows different then naive factorization for {text}')

  def test_cps_matches_naive(self):
    for text in ['a', 'ab', 'aaaaaaaa', 'aabbaabbbaaabbb',
                 'abasjdnaikjsdndwa']:
      self.check_cps_factorization(text)

  def test_cps_factors(self):
    factors = lz77_cps.factorize('#aabbaabba', 9)
    self.assertEqual([(f.length, f.literal) for f in factors],
                     [(0, 'a'), (1, 'b'), (1, 'a'), (3, 'a')])
    self.assertEqual([f.position for f in factors], [1, 1, 3, 2])

  def test_cps_parameters_without_factors(self):
    _, parameters, _, _ = lz77_cps.compress('#1234', 4, ['1', '2', '3', '4'])
    self.assertEqual(
        (parameters.n, parameters.max_length, parameters.Ll), (4, 0, 0))
    self.assertEqual(parameters.Lc, 1 + parameters.Lp)


  def check_round_trip(self, text, compress, decompress, A = None):
    w = '#' + text
    stream, parameters, A, stats = compress(w, len(text), A)
    self.assertEqual(decompress(stream, len(text), parameters, A), w,
        f'Round trip failed for {text}')
    self.assertEqual(stats.source_symbols, len(text),
        f'Wrong number of source symbols counted for {text}')

  @parameterized.parameterized.expand(LEMPEL_ZIV_CODECS)
  def test_round_trip_corners(self, _, compress, decompress):
    self.check_round_trip('', compress, decompress, ['a', 'b'])
    self.check_round_trip('a', compress, decompress, ['a', 'b'])
    self.check_round_trip('ab', compress, decompress)
    self.check_round_trip('aaaaaaaa', compress, decompress, ['a', 'b'])
    self.check_round_trip('abbaabbbaaabab', compress, decompress)
    self.check_round_trip('aacaacabcabaaac', compress, decompress)
    self.check_round_trip('oasuieancojlasodiujdn', compress, decompress)

  @parameterized.parameterized.expand(LEMPEL_ZIV_CODECS)
  def test_round_trip_named_words(self, _, compress, decompress):
    self.check_round_trip(
        named.fibonacci_word(10)[1:], compress, decompress)
    self.check_round_trip(named.thue_word(6)[1:], compress, decompress)

  @parameterized.parameterized.expand(LEMPEL_ZIV_CODECS)
  @run_large
  def test_round_trip_named_words_large(self, _, compress, decompress):
    self.check_round_trip(
        named.fibonacci_word(18)[1:], compress, decompress)
    self.check_round_trip(named.thue_word(10)[1:], compress, decompress)

  @parameterized.parameterized.expand(LEMPEL_ZIV_CODECS)
  @run_large
  def test_round_trip_random(self, _, compress, decompress):
    T, n, A = 10, 2000, ['a', 'b', 'c']
    for _ in range(T):
      self.check_round_trip(
          rand.random_word(n, A)[1:], compress, decompress, A)

