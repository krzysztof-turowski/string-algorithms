import itertools
import os
import unittest

import parameterized

from generator import rand
from string_indexing import farach, suffix_array, suffix_tree

SUFFIX_ARRAY_ALGORITHMS = [
    [ 'Karp-Miller-Rosenberg', suffix_array.prefix_doubling ],
    [ 'Karkkainen-Sanders', suffix_array.skew ],
    [ 'Farach', farach.suffix_array ],
    [ 'Larsson-Sadakane', suffix_array.larsson_sadakane ],
    [ 'Ko-Aluru', suffix_array.small_large ],
    [ 'Zhang-Nong-Chan', suffix_array.induced_sorting ],
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
    self.check_suffix_array(
        '#abaaabbabbba', 12, [13, 12, 3, 4, 1, 5, 8, 11, 2, 7, 10, 6, 9],
        algorithm)
    self.check_suffix_array('#abaaba', 6, [7, 6, 3, 4, 1, 5, 2], algorithm)
    self.check_suffix_array(
        '#abcdefghabce', 12, [13, 1, 9, 2, 10, 3, 11, 4, 12, 5, 6, 7, 8],
        algorithm)
    self.check_suffix_array(
        '#abcdefgh', 8, [9, 1, 2, 3, 4, 5, 6, 7, 8], algorithm)
    self.check_suffix_array('#bacaca', 6, [7, 6, 4, 2, 1, 5, 3], algorithm)
    self.check_suffix_array(
        '#aabbacbc', 8, [9, 1, 2, 5, 4, 3, 7, 8, 6], algorithm)
    self.check_suffix_array(
        '#abcaaabbcaaaaba', 15,
        [16, 15, 10, 11, 4, 12, 5, 13, 6, 1, 14, 7, 8, 2, 9, 3], algorithm)
    self.check_suffix_array(
        '#aaabcbaaabdaaabcbaabcba', 23,
        [24, 23, 1, 12, 7, 18, 2, 13, 8, 19, 3, 14, 9, 22, 6, 17, 20, 4, 15,
         10, 21, 5, 16, 11],
        algorithm)
    self.check_suffix_array(
        '#aabbacbacbaabcbbc', 17,
        [18, 1, 11, 2, 12, 8, 5, 10, 7, 4, 3, 15, 16, 13, 17, 9, 6, 14],
        algorithm)

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
