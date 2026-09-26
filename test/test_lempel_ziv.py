import itertools
import os
import unittest
import string

from compression import (lempel_ziv, lz77_cps, lz77_sliding_window,
                         lz78_block, lz77_kkp3, lz78)
from compression.core import parser

import parameterized

from generator import rand, named

from common import numeric

from string_indexing import lpf

def lz77_sliding_window_as_triples(w, n, A):
  """
  Replaces codeword stream with (position, length, symbol) triples
  """
  stream, parameters, A, _ = lz77_sliding_window.compress(
      w, n, 2 * max(n, 1), max(n, 1), A)
  triples, i = [], 0
  while i < len(stream):
    C = stream[i:i + parameters.Lc]
    position = numeric.from_radix(C[:parameters.Lp], parameters.alpha) + 1
    length = numeric.from_radix(
        C[parameters.Lp:parameters.Lp + parameters.Ll], parameters.alpha)
    triples.append((parameters.window_size - position + 1 if length else 0,
                    length, A[C[-1]]))
    i += parameters.Lc
  return triples

def lz78_block_as_pairs(w, n, A):
  """
  Replaces the bit stream as (position, symbol) pairs
  """
  encoded, parameters, A, _ = lz78_block.compress(w, n, max(n, 1), A)
  reader = lz78_block.BitReader(encoded)
  pairs, j = [], 1
  while reader.pos < encoded.bits:
    I = reader.read(lz78_block.codeword_width(parameters, j))
    parent, a = divmod(I, parameters.alpha)
    pairs.append((parent, A[a]))
    j += 1
  return pairs

def lz77_sliding_window_compress(w, n, A):
  return lz77_sliding_window.compress(w, n, 1024, 32, A)

def lz78_block_compress(w, n, A):
  return lz78_block.compress(w, n, 1024, A)

def naive_lz77_compress(w, n, A = None):
  return lempel_ziv.lz77(w, n), None, A, None

def naive_lz77_decompress(code, _n, _parameters, _A):
  return lempel_ziv.inverse_lz77(code)

def lz78_dictionary_compress(w, _n, A = None):
  return lz78.lz78_compress(w, parser.GreedyOutputParser), None, A, None

def lz78_dictionary_decompress(code, _n, _parameters, _A):
  return '#' + lz78.lz78_decompress(code)

def naive_lz77_as_pairs(w, n, _A):
  return [(length, literal) for _, length, literal in lempel_ziv.lz77(w, n)]

def lz77_sliding_window_as_pairs(w, n, A):
  return [(length, literal)
          for _, length, literal in lz77_sliding_window_as_triples(w, n, A)]

def lz77_cps_as_pairs(w, n, _A):
  return [(f.length, f.literal) for f in lz77_cps.factorize(w, n)]

def lz77_kkp3_as_pairs(w, n, _A):
  return [(f.length, f.literal) for f in lz77_kkp3.factorize(w, n)]

LEMPEL_ZIV_77_CODECS = [
  [
    'LZ77 sliding window',
    lz77_sliding_window_compress,
    lz77_sliding_window.decompress,
  ],
  [
    'LZ77 with CPS factorization',
    lz77_cps.compress,
    lz77_cps.decompress
  ],
  [
    'LZ77 with KKP3 factorization',
    lz77_kkp3.compress,
    lz77_kkp3.decompress
  ],
  [ 'naive LZ77', naive_lz77_compress, naive_lz77_decompress ],
]

LEMPEL_ZIV_78_CODECS = [
  [ 'LZ78 block', lz78_block_compress, lz78_block.decompress ],
  [
    'LZ78 dictionary',
    lz78_dictionary_compress,
    lz78_dictionary_decompress
  ],
]

LEMPEL_ZIV_FACTORIZATIONS = [
  [ 'naive', lempel_ziv.naive_factorization ],
  [ 'Crochemore-Ilie-Smyth', lempel_ziv.crochemore_ilie_smyth ],
]

LEMPEL_ZIV_77_FACTORIZATIONS = [
  [ 'naive LZ77', naive_lz77_as_pairs ],
  [ 'LZ77 sliding window', lz77_sliding_window_as_pairs ],
  [ 'LZ77 with CPS factorization', lz77_cps_as_pairs ],
  [ 'LZ77 with KKP3 factorization', lz77_kkp3_as_pairs ],
]

class TestLempelZiv(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_round_trip(self, text, compress, decompress, A = None):
    w = '#' + text
    code, parameters, A, _ = compress(w, len(text), A)
    self.assertEqual(decompress(code, len(text), parameters, A), w,
        f'Round trip failed for {text}')

  @parameterized.parameterized.expand(
      LEMPEL_ZIV_77_CODECS + LEMPEL_ZIV_78_CODECS)
  def test_round_trip_corners(self, _, compress, decompress):
    self.check_round_trip('', compress, decompress, ['a', 'b'])
    self.check_round_trip('a', compress, decompress, ['a', 'b'])
    self.check_round_trip('ab', compress, decompress)
    self.check_round_trip('aaaaaaaa', compress, decompress, ['a', 'b'])
    self.check_round_trip('abbaabbbaaabab', compress, decompress)
    self.check_round_trip('aacaacabcabaaac', compress, decompress)
    self.check_round_trip('oasuieancojlasodiujdn', compress, decompress)

  @parameterized.parameterized.expand(
      LEMPEL_ZIV_77_CODECS + LEMPEL_ZIV_78_CODECS)
  def test_round_trip_named_words(self, _, compress, decompress):
    self.check_round_trip(
        named.fibonacci_word(10)[1:], compress, decompress)
    self.check_round_trip(named.thue_word(6)[1:], compress, decompress)

  @parameterized.parameterized.expand(
      LEMPEL_ZIV_77_CODECS + LEMPEL_ZIV_78_CODECS)
  @run_large
  def test_round_trip_named_words_large(self, _, compress, decompress):
    self.check_round_trip(
        named.fibonacci_word(18)[1:], compress, decompress)
    self.check_round_trip(named.thue_word(10)[1:], compress, decompress)

  @parameterized.parameterized.expand(
      LEMPEL_ZIV_77_CODECS + LEMPEL_ZIV_78_CODECS)
  @run_large
  def test_round_trip_random(self, _, compress, decompress):
    T, n, A = 10, 2000, ['a', 'b', 'c']
    for _ in range(T):
      self.check_round_trip(
          rand.random_word(n, A)[1:], compress, decompress, A)

# pylint: disable=too-many-public-methods
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

  @parameterized.parameterized.expand(LEMPEL_ZIV_FACTORIZATIONS)
  @run_large
  def test_lz_factorization_random(self, _, algorithm):
    T, n, A = 100, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_factorization(
          text, lempel_ziv.naive_factorization('#' + text, len(text)),
          algorithm)

  @parameterized.parameterized.expand(LEMPEL_ZIV_FACTORIZATIONS)
  @run_large
  def test_lz_factorization_random_short_strings(self, _, algorithm):
    T, n, A = 5, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_factorization(
          text, lempel_ziv.naive_factorization('#' + text, len(text)),
          algorithm)

  @parameterized.parameterized.expand(LEMPEL_ZIV_FACTORIZATIONS)
  @run_large
  def test_lz_factorization_random_cyclic(self, _, algorithm):
    T, n, A = 10, 200, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:] * 10
      self.check_factorization(
          text, lempel_ziv.naive_factorization('#' + text, len(text)),
          algorithm)

  @parameterized.parameterized.expand(LEMPEL_ZIV_FACTORIZATIONS)
  @run_large
  def test_lz_factorization_random_big_alphabet(self, _, algorithm):
    T, n, A = 100, 500, string.ascii_letters + string.digits
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_factorization(
          text, lempel_ziv.naive_factorization('#' + text, len(text)),
          algorithm)

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

  def check_sliding_window_matches_naive(self, text):
    w, n = '#' + text, len(text)
    A = sorted(set(text)) if len(set(text)) > 1 else ['a', 'b']
    self.assertEqual(
        lz77_sliding_window_as_triples(w, n, A), lempel_ziv.lz77(w, n),
        f'lz77_sliding_window does not match lempel_ziv.lz77 for {text}')

  def test_sliding_window_matches_naive_random(self):
    T, n, A = 5, 200, ['a', 'b', 'c', 'd']
    for _ in range(T):
      self.check_sliding_window_matches_naive(rand.random_word(n, A)[1:])

  @run_large
  def test_sliding_window_matches_naive_random_large(self):
    T, n, A = 5, 20000, ['a', 'b', 'c', 'd']
    for _ in range(T):
      self.check_sliding_window_matches_naive(rand.random_word(n, A)[1:])

  def check_cps_factorization(self, text):
    w, n = '#' + text, len(text)
    _, LEN = lz77_cps.chen_puglisi_smyth_factorization(w, n)
    self.assertEqual(LEN, lpf.naive(w, n),
        f'CPS shows different then naive factorization for {text}')

  def check_lz77_factorization(self, text, factorization):
    w, n = '#' + text, len(text)
    A = sorted(set(text)) if len(set(text)) > 1 else ['a', 'b']
    self.assertEqual(
        factorization(w, n, A),
        [(length, literal) for _, length, literal in lempel_ziv.lz77(w, n)],
        f'the factorization does not match lempel_ziv.lz77 for {text}')

  @parameterized.parameterized.expand(LEMPEL_ZIV_77_FACTORIZATIONS)
  def test_lz77_factorizations_agree_random(self, _, factorization):
    T, n, A = 5, 200, ['a', 'b', 'c']
    for _ in range(T):
      self.check_lz77_factorization(rand.random_word(n, A)[1:], factorization)

  @parameterized.parameterized.expand(LEMPEL_ZIV_77_FACTORIZATIONS)
  @run_large
  def test_lz77_factorizations_agree_random_large(self, _, factorization):
    T, n, A = 5, 2000, ['a', 'b', 'c', 'd']
    for _ in range(T):
      self.check_lz77_factorization(rand.random_word(n, A)[1:], factorization)

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

  def test_kkp_factors(self):
    factors = lz77_kkp3.factorize('#zzzzzipzip', 10)
    self.assertEqual([(f.length, f.literal) for f in factors],
                     [(0, 'z'), (4, 'i'), (0, 'p'), (2, 'p')])

# pylint: disable=too-many-public-methods
class TestLempelZiv78(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_lz78_block_codeword_width(self):
    parameters = lz78_block.make_parameters(2, 16)
    self.assertEqual(
        [lz78_block.codeword_width(parameters, j) for j in [1, 2, 3, 4, 5]],
        [1, 2, 3, 3, 4])
    parameters = lz78_block.make_parameters(3, 16)
    self.assertEqual(
        [lz78_block.codeword_width(parameters, j) for j in [1, 2, 3]],
        [2, 3, 4])

  def check_block_matches_dictionary(self, text):
    w, n = '#' + text, len(text)
    A = sorted(set(text)) if len(set(text)) > 1 else ['a', 'b']
    self.assertEqual(
        lz78_block_as_pairs(w, n, A),
        lz78.lz78_compress(w, parser.GreedyOutputParser),
        f'lz78_block does not match lz78.lz78_compress for {text}')

  def test_block_matches_dictionary_random(self):
    T, n, A = 5, 200, ['a', 'b', 'c', 'd']
    for _ in range(T):
      self.check_block_matches_dictionary(rand.random_word(n, A)[1:])

  @run_large
  def test_block_matches_dictionary_random_large(self):
    T, n, A = 5, 20000, ['a', 'b', 'c', 'd']
    for _ in range(T):
      self.check_block_matches_dictionary(rand.random_word(n, A)[1:])
