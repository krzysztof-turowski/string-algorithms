import itertools
import os
import unittest

import parameterized

from generator import rand
from approximate_string_matching import matching_with_dont_cares

DETERMINISTIC_ALGORITHMS = [
    [ 'basic FFT', matching_with_dont_cares.basic_fft ],
    [ 'Clifford-Clifford', matching_with_dont_cares.clifford_clifford ],
    [ 'Clifford-Clifford with split',
      matching_with_dont_cares.clifford_clifford_parts ],
    [ 'Naive', matching_with_dont_cares.naive ],
    [ 'Fischer-Paterson', matching_with_dont_cares.fischer_paterson ],
    [ 'Sperner', matching_with_dont_cares.sperner ],
]

RANDOMIZED_ALGORITHMS = [
    [ 'Indyk', matching_with_dont_cares.indyk ],
    [ 'Kalai', matching_with_dont_cares.kalai ],
]

ALL_ALGORITHMS = DETERMINISTIC_ALGORITHMS + RANDOMIZED_ALGORITHMS

class TestExactMatchingWithDontCares(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_matches(self, t, w, n, m, reference, algorithm):
    self.assertEqual(list(algorithm(t, w, n, m)), reference)

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  def test_examples(self, _, algorithm):
    self.check_matches('#abbabaaa', '#ab', 8, 2, [1, 4], algorithm)
    self.check_matches('#abbabaaa', '#??a', 8, 3, [2, 4, 5, 6], algorithm)
    self.check_matches('#aa', '#a', 2, 1, [1, 2], algorithm)
    self.check_matches('#abcdef', '#x', 6, 1, [], algorithm)
    self.check_matches('#abcde', '#???', 5, 3, [1, 2, 3], algorithm)
    self.check_matches('#aaaaa', '#a?a', 5, 3, [1, 2, 3], algorithm)
    self.check_matches('#xyzabcd', '#?bc?', 7, 4, [4], algorithm)
    self.check_matches('#test', '#t?st', 4, 4, [1], algorithm)

  @parameterized.parameterized.expand(ALL_ALGORITHMS)
  @run_large
  def test_random_exact_string_matching(self, _, algorithm):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A + ['?'])
      reference = list(matching_with_dont_cares.basic_fft(t, w, n, m))
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
            reference = list(matching_with_dont_cares.basic_fft(t, w, n, m))
            self.check_matches(t, w, n, m, reference, algorithm)