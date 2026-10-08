import functools
import itertools
import os
import random
import unittest

import parameterized

from generator import rand
from approximate_string_matching import matching_with_dont_cares
from common.fft import fft_boolean
from common.gf2 import gf2_boolean

DETERMINISTIC_ALGORITHMS = [
    [ 'naive', matching_with_dont_cares.naive ],
    [ 'basic FFT', matching_with_dont_cares.basic_fft ],
    [ 'Sperner', matching_with_dont_cares.sperner ],
    [ 'Fischer-Paterson', matching_with_dont_cares.fischer_paterson ],
    [ 'Clifford-Clifford', matching_with_dont_cares.clifford_clifford ],
    [ 'Clifford-Clifford with split',
      functools.partial(
        matching_with_dont_cares.fft_by_parts,
        algorithm = matching_with_dont_cares.clifford_clifford) ],
]

RANDOMIZED_ALGORITHMS = [
    [ 'Indyk with FFT',
      functools.partial(
        matching_with_dont_cares.indyk, c = 7,
        boolean_convolve = fft_boolean) ],
    [ 'Indyk over GF(2)',
      functools.partial(
        matching_with_dont_cares.indyk, c = 16,
        boolean_convolve = gf2_boolean) ],
    [ 'Kalai', matching_with_dont_cares.kalai ],
]

ALL_ALGORITHMS = DETERMINISTIC_ALGORITHMS + RANDOMIZED_ALGORITHMS

LARGE_ALPHABET_ALGORITHMS = [
    [ name, algorithm ] for name, algorithm in ALL_ALGORITHMS
    if not name.startswith(('basic FFT', 'Fischer-Paterson'))]

class TestExactMatchingWithDontCares(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_matches(self, t, w, n, m, reference, algorithm):
    def _function(candidate):
      if isinstance(candidate, functools.partial):
        return candidate.func
      return candidate

    if any(
        _function(algorithm) is _function(candidate)
        for _, candidate in RANDOMIZED_ALGORITHMS):
      self.check_monte_carlo_matches(t, w, n, m, reference, algorithm)
    else:
      self.assertEqual(list(algorithm(t, w, n, m)), reference)

  def check_monte_carlo_matches(
      self, t, w, n, m, reference, algorithm, k = 5):
    best = []
    for _ in range(k):
      matches = list(algorithm(t, w, n, m))
      self.assertTrue(set(reference).issubset(matches))
      best = matches if len(best) < len(matches) else best
    self.assertEqual(best, reference)

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  def test_examples(self, _, algorithm):
    random.seed(0)
    self.check_matches('#abbabaaa', '#ab', 8, 2, [1, 4], algorithm)
    self.check_matches('#abbabaaa', '#??a', 8, 3, [2, 4, 5, 6], algorithm)
    self.check_matches('#aa', '#a', 2, 1, [1, 2], algorithm)
    self.check_matches('#abcdef', '#x', 6, 1, [], algorithm)
    self.check_matches('#abcde', '#???', 5, 3, [1, 2, 3], algorithm)
    self.check_matches('#aaaaa', '#a?a', 5, 3, [1, 2, 3], algorithm)
    self.check_matches('#xyzabcd', '#?bc?', 7, 4, [4], algorithm)
    self.check_matches('#test', '#t?st', 4, 4, [1], algorithm)
    self.check_matches('#abc', '#', 3, 0, [], algorithm)
    self.check_matches('#a', '#ab', 1, 2, [], algorithm)
    self.check_matches('#', '#a', 0, 1, [], algorithm)
    self.check_matches('#?', '#?', 1, 1, [1], algorithm)
    self.check_matches('#????', '#??', 4, 2, [1, 2, 3], algorithm)
    self.check_matches('#a?aa', '#aa', 4, 2, [1, 2, 3], algorithm)

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  @run_large
  def test_long_unary_text(self, _, algorithm):
    random.seed(0)
    n, m = 40000, 20000
    t, w = '#' + 'a' * n, '#' + 'a' * m
    self.check_matches(t, w, n, m, list(range(1, n - m + 2)), algorithm)

  @staticmethod
  def random_instance(n, m, A):
    '''Random text and its fragment with extra wildcards as the word'''
    t = ''.join(random.choices(A + ['?'], [1] * len(A) + [0.2], k = n))
    offset = random.randrange(n - m + 1)
    w = ''.join(character if random.random() > 0.1 else '?'
                for character in t[offset:offset + m])
    return '#' + t, '#' + w, [offset + 1]

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  @run_large
  def test_long_random_text(self, _, algorithm):
    n, m, A = 40000, 20000, ['a', 'b', 'c', 'd']
    t, w, reference = self.random_instance(n, m, A)
    self.check_matches(t, w, n, m, reference, algorithm)

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  @run_large
  def test_random_large_alphabet(self, _, algorithm):
    T_tests, n, m = 50, 200, 15
    A = [chr(i) for i in range(97, 123)]
    for _ in range(T_tests):
      t, w = rand.random_word(n, A), rand.random_word(m, A + ['?'])
      reference = list(matching_with_dont_cares.basic_fft(t, w, n, m))
      self.check_matches(t, w, n, m, reference, algorithm)

  @parameterized.parameterized.expand(DETERMINISTIC_ALGORITHMS)
  @run_large
  def test_all_exact_string_matching(self, _, algorithm):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for t in itertools.product(A, repeat = n):
          t = '#' + ''.join(t)
          for w in itertools.product(A + ['?'], repeat = m):
            w = '#' + ''.join(w)
            reference = list(
              matching_with_dont_cares.basic_fft(t, w, n, m))
            self.check_matches(t, w, n, m, reference, algorithm)

  @parameterized.parameterized.expand(LARGE_ALPHABET_ALGORITHMS)
  @run_large
  def test_long_random_text_large_alphabet(self, _, algorithm):
    n, m = 40000, 20000
    A = [chr(256 + i) for i in range(2000)]
    t, w, reference = self.random_instance(n, m, A)
    self.check_matches(t, w, n, m, reference, algorithm)

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  @run_large
  def test_random_exact_string_matching(self, _, algorithm):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A + ['?'])
      reference = list(matching_with_dont_cares.basic_fft(t, w, n, m))
      self.check_matches(t, w, n, m, reference, algorithm)
