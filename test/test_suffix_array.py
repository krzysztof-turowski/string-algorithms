import itertools
import os
import unittest

import parameterized

from generator import rand
from string_indexing import farach, suffix_array, suffix_tree, \
                            sl_suffix_array

SUFFIX_ARRAY_ALGORITHMS = [
    [
        'Karp-Miller-Rosenberg',
        suffix_array.prefix_doubling,
    ],
    [
        'Karkkainen-Sanders',
        suffix_array.skew,
    ],
    [
        'Farach',
        farach.suffix_array,
    ],
    [
        'Larsson-Sadakane',
        suffix_array.larsson_sadakane,
    ],
    [
        'Ko-Aluru',
        sl_suffix_array.small_large,
    ],
    [
        'Zhang-Nong-Chan',
        suffix_array.induced_sorting,
    ],
    [
        'from suffix tree',
        lambda t, n: suffix_array.from_suffix_tree(
            suffix_tree.mccreight(t, n)[0], n),
    ]
]

class TestSuffixArrays(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_suffix_array(self, t, n, reference, algorithm):
    self.assertEqual(algorithm(t, n), reference)

  @parameterized.parameterized.expand(SUFFIX_ARRAY_ALGORITHMS)
  def test_examples(self, _, algorithm):
    self.check_suffix_array('#abaaba', 6, [7, 6, 3, 4, 1, 5, 2], algorithm)
    self.check_suffix_array('#banana', 6, [7, 6, 4, 2, 1, 5, 3], algorithm)
    self.check_suffix_array(
        '#abaaaaaaa', 9, [10, 9, 8, 7, 6, 5, 4, 3, 1, 2], algorithm)
    self.check_suffix_array(
        '#yabbadabbado', 12, [13, 2, 7, 5, 10, 4, 9, 3, 8, 6, 11, 12, 1],
        algorithm)
    self.check_suffix_array(
        '#aabaabaabba', 11, [12, 11, 1, 4, 7, 2, 5, 8, 10, 3, 6, 9], algorithm)
    self.check_suffix_array(
        '#hcrgpfeargibbpq', 15,
        [16, 8, 12, 13, 2, 7, 6, 10, 4, 1, 11, 5, 14, 15, 9, 3], algorithm)
    self.check_suffix_array(
        '#obdkbgaobg', 10, [11, 7, 2, 9, 5, 3, 10, 6, 4, 1, 8], algorithm)

  @parameterized.parameterized.expand(SUFFIX_ARRAY_ALGORITHMS)
  @run_large
  def test_random_suffix_array(self, _, algorithm):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = suffix_array.naive(t, n)
      self.check_suffix_array(t, n, reference, algorithm)

  @parameterized.parameterized.expand(SUFFIX_ARRAY_ALGORITHMS)
  @run_large
  def test_all_suffix_array(self, _, algorithm):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = suffix_array.naive(t, n)
        self.check_suffix_array(t, n, reference, algorithm)
