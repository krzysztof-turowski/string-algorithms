import itertools
import os
import unittest

import parameterized

from generator import rand
from string_indexing import farach, lcp, suffix_array, suffix_tree

LCP_ARRAY_ALGORITHMS = [
    [
        'Farach',
        farach.lcp_array,
    ],
    [
        'Kasai',
        lambda t, n: lcp.kasai(
            suffix_array.prefix_doubling(t, n), t, n),
    ],
    [
        'from suffix tree',
        lambda t, n: lcp.from_suffix_tree(suffix_tree.mccreight(t, n)[0]),
    ],
    [
        'from suffix array',
        lambda t, n: lcp.from_suffix_array(
            suffix_array.prefix_doubling(t, n), t, n),
    ],
    [
        'from PLCP#a',
        lambda t, n: lcp.convert_plcp_to_lcp(
            lcp.build_plcp_a(suffix_array.prefix_doubling(t, n), t, n),
            suffix_array.prefix_doubling(t, n), t),
    ],
    [
        'from PLCP#b',
        lambda t, n: lcp.convert_plcp_to_lcp(
            lcp.build_plcp_b(suffix_array.prefix_doubling(t, n), t, n),
            suffix_array.prefix_doubling(t, n), t),
    ],
    [
        'from sparse PLCP#a',
        lambda t, n: lcp.convert_plcp_to_lcp(
            lcp.build_plcp_a(suffix_array.prefix_doubling(t, n), t, n, q = 2),
            suffix_array.prefix_doubling(t, n), t, q = 2),
    ],
    [
        'from sparse PLCP#b',
        lambda t, n: lcp.convert_plcp_to_lcp(
            lcp.build_plcp_b(suffix_array.prefix_doubling(t, n), t, n, q = 2),
            suffix_array.prefix_doubling(t, n), t, q = 2),
    ]
]

class TestLcpArrays(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_lcp_array(self, t, n, reference, algorithm):
    self.assertEqual(algorithm(t, n), reference)

  @parameterized.parameterized.expand(LCP_ARRAY_ALGORITHMS)
  def test_examples(self, _, algorithm):
    self.check_lcp_array('#banana', 6, [-1, 0, 1, 3, 0, 0, 2], algorithm)
    self.check_lcp_array(
        '#abaaabbabbba', 12, [-1, 0, 1, 2, 1, 2, 3, 0, 2, 2, 1, 3, 2],
        algorithm)
    self.check_lcp_array('#abaaba', 6, [-1, 0, 1, 1, 3, 0, 2], algorithm)
    self.check_lcp_array(
        '#abcdefghabce', 12, [-1, 0, 3, 0, 2, 0, 1, 0, 0, 1, 0, 0, 0],
        algorithm)
    self.check_lcp_array(
        '#abcdefgh', 8, [-1, 0, 0, 0, 0, 0, 0, 0, 0], algorithm)
    self.check_lcp_array('#bacaca', 6, [-1, 0, 1, 3, 0, 0, 2], algorithm)
    self.check_lcp_array(
        '#aabbacbc', 8, [-1, 0, 1, 1, 0, 1, 1, 0, 1], algorithm)
    self.check_lcp_array(
        '#abcaaabbcaaaaba', 15,
        [-1, 0, 1, 3, 4, 2, 3, 1, 2, 2, 0, 1, 1, 5, 0, 4], algorithm)
    self.check_lcp_array(
        '#aaabcbaaabdaaabcbaabcba', 23,
        [-1, 0, 1, 8, 4, 2, 6, 7, 3, 1, 5, 6, 2, 0, 2, 3, 1, 4, 5, 1,
         0, 3, 4, 0],
        algorithm)
    self.check_lcp_array(
        '#aabbacbacbaabcbbc', 17,
        [-1, 0, 3, 1, 2, 1, 4, 0, 2, 5, 1, 2, 1, 2, 0, 1, 3, 2], algorithm)

  @parameterized.parameterized.expand(LCP_ARRAY_ALGORITHMS)
  @run_large
  def test_random_lcp_array(self, _, algorithm):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = lcp.from_suffix_array(
          suffix_array.prefix_doubling(t, n), t, n)
      self.check_lcp_array(t, n, reference, algorithm)

  @parameterized.parameterized.expand(LCP_ARRAY_ALGORITHMS)
  @run_large
  def test_all_lcp_array(self, _, algorithm):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = lcp.from_suffix_array(
            suffix_array.prefix_doubling(t, n), t, n)
        self.check_lcp_array(t, n, reference, algorithm)

class TestLcpLr(unittest.TestCase):
  def check_lcp_lr(self, text, n, reference):
    lcp_lr = lcp.build_lcp_lr(
        lcp.kasai(suffix_array.skew(text, n), text, n), n)
    self.assertEqual(lcp_lr, reference)

  def test_construction(self):
    self.check_lcp_lr("#banana", 6, {
        (1, 2): 1, (2, 3): 3, (1, 3): 1, (3, 4): 0, (4, 5): 0, (5, 6): 2,
        (4, 6): 0, (3, 6): 0, (1, 6): 0})

class TestPlcp(unittest.TestCase):
  def check_plcp(self, text, n, reference):
    plcp = lcp.build_plcp_a(suffix_array.skew(text, n), text, n)
    self.assertEqual(plcp, reference)
    plcp = lcp.build_plcp_b(suffix_array.skew(text, n), text, n)
    self.assertEqual(plcp, reference)

  def test_construction(self):
    self.check_plcp("#banana", 6, [0, 0, 3, 2, 1, 0, 0])
    self.check_plcp('#abaaabbabbba', 12,
      [0, 1, 2, 1, 2, 2, 3, 2, 3, 2, 1, 0, 0])
