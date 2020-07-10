import itertools
import os
import unittest

import parameterized

from generator import rand
from approximate_string_matching import matching_with_dont_cares

MATCHING_WITH_DONT_CARE_ALGORITHMS = [
    [ 'basic FFT', matching_with_dont_cares.basic_fft ],
    [ 'Clifford-Clifford', matching_with_dont_cares.clifford_clifford ],
    [ 'Clifford-Clifford with split',
      matching_with_dont_cares.clifford_clifford_parts ],
]

class TestExactMatchingWithDontCares(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_matches(self, t, w, n, m, reference, algorithm):
    self.assertEqual(list(algorithm(t, w, n, m)), reference)

  @parameterized.parameterized.expand(MATCHING_WITH_DONT_CARE_ALGORITHMS)
  def test_examples(self, _, algorithm):
    self.check_matches('#abbabaaa', '#ab', 8, 2, [1, 4], algorithm)
    self.check_matches('#abbabaaa', '#??a', 8, 3, [2, 4, 5, 6], algorithm)
    self.check_matches('#aa', '#a', 2, 1, [1, 2], algorithm)

  @parameterized.parameterized.expand(MATCHING_WITH_DONT_CARE_ALGORITHMS)
  @run_large
  def test_random_exact_string_matching(self, _, algorithm):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A + ['?'])
      reference = list(matching_with_dont_cares.basic_fft(t, w, n, m))
      self.check_matches(t, w, n, m, reference, algorithm)

  @parameterized.parameterized.expand(MATCHING_WITH_DONT_CARE_ALGORITHMS)
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
