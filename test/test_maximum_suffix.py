import itertools
import os
import unittest

import parameterized

from generator import rand
from string_indexing import suffix_array
from lyndon import maximum_suffix

MAXIMUM_SUFFIX_ALGORITHMS = [
    [ 'from prefix suffix', maximum_suffix.from_prefix_suffix ],
    [ 'constant space', maximum_suffix.constant_space ],
    [
        'from suffix array',
        lambda t, n: maximum_suffix.from_suffix_array(
            suffix_array.naive(t, n), t, n)
    ],
]

class TestMaximumSuffix(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_maximum_suffix(self, t, n, reference, algorithm):
    self.assertEqual(
        algorithm(t, n),
        reference,
        'Algorithm: {}'.format(algorithm.__name__))

  @parameterized.parameterized.expand(MAXIMUM_SUFFIX_ALGORITHMS)
  def test_maximum_suffix(self, _, algorithm):
    self.check_maximum_suffix('#abaaba', 6, (2, 3), algorithm)
    self.check_maximum_suffix('#banana', 6, (3, 2), algorithm)
    self.check_maximum_suffix('#abaaaaaaa', 9, (2, 8), algorithm)
    self.check_maximum_suffix('#yabbadabbado', 12, (1, 12), algorithm)
    self.check_maximum_suffix('#aabaabaabba', 11, (9, 3), algorithm)
    self.check_maximum_suffix('#eembambmaaa', 11, (6, 6), algorithm)

  @parameterized.parameterized.expand(MAXIMUM_SUFFIX_ALGORITHMS)
  @run_large
  def test_random_maximum_suffix(self, _, algorithm):
    T, n, A = 100, 1000, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = maximum_suffix.naive(t, n)
      self.check_maximum_suffix(t, n, reference, algorithm)

  @parameterized.parameterized.expand(MAXIMUM_SUFFIX_ALGORITHMS)
  @run_large
  def test_all_maximum_suffix(self, _, algorithm):
    N, A = 14, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = maximum_suffix.naive(t, n)
        self.check_maximum_suffix(t, n, reference, algorithm)
