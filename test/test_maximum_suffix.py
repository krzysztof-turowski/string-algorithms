import itertools
import os
import unittest

from generator import rand
from string_indexing import suffix_array
from lyndon import maximum_suffix

MAXIMUM_SUFFIX_ALGORITHMS = [
    maximum_suffix.from_prefix_suffix,
    maximum_suffix.constant_space,
]

class TestMaximumSuffix(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_maximum_suffix(self, t, n, reference):
    for algorithm in MAXIMUM_SUFFIX_ALGORITHMS:
      self.assertEqual(
          algorithm(t, n),
          reference,
          'Algorithm: {0}'.format(algorithm.__name__))
    self.assertEqual(
        suffix_array.naive(t, n)[-1],
        reference,
        'Maximum suffix from suffix array')

  def test_maximum_suffix(self):
    self.check_maximum_suffix('#abaaba', 6, 2)
    self.check_maximum_suffix('#banana', 6, 3)
    self.check_maximum_suffix('#abaaaaaaa', 9, 2)
    self.check_maximum_suffix('#yabbadabbado', 12, 1)
    self.check_maximum_suffix('#aabaabaabba', 11, 9)
    self.check_maximum_suffix('#eembambmaaa', 11, 6)

  @run_large
  def test_random_maximum_suffix(self):
    T, n, A = 100, 1000, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = suffix_array.naive(t, n)[-1]
      self.check_maximum_suffix(t, n, reference)

  @run_large
  def test_all_maximum_suffix(self):
    N, A = 14, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = suffix_array.naive(t, n)[-1]
        self.check_maximum_suffix(t, n, reference)
