import itertools
import os
import unittest

import parameterized

from generator import rand
from exact_string_matching import forward, backward, other
from string_indexing import lcp, suffix_tree, suffix_array

def lcp_lr_contains(t, w, n, m):
  SA = suffix_array.skew(t, n)
  LCP_LR = lcp.build_lcp_lr(lcp.kasai(SA, t, n), n)
  return lcp.contains(SA, LCP_LR, t, w, n, m)

EXACT_STRING_MATCHING_ALGORITHMS = [
    [ 'Morris-Pratt', forward.morris_pratt ],
    [ 'Knuth-Morris-Pratt', forward.knuth_morris_pratt ],
    [ 'Boyer-Moore', backward.boyer_moore ],
    [ 'Boyer-Moore with bad shifts', backward.boyer_moore_bad_shift ],
    [ 'Boyer-Moore-Galil', backward.boyer_moore_galil ],
    [ 'Turbo-Boyer-Moore', backward.turbo_boyer_moore ],
    [ 'bad shift heuristic', backward.bad_shift_heuristic ],
    [ 'quick search heuristic', backward.quick_search ],
    [
        'Boyer-Moore-Apostolico-Giancarlo',
        backward.boyer_moore_apostolico_giancarlo
    ],
    [ 'Horspool', backward.horspool ],
    [ 'Karp-Rabin', other.karp_rabin ],
    [ 'fast-on-average', other.fast_on_average ],
    [ 'two-way constant space', other.two_way ],
    [
        'suffix tree',
        lambda t, w, n, m: suffix_tree.contains(
            suffix_tree.mccreight(t, n)[0], t, w, n, m),
    ],
    [
        'suffix array',
        lambda t, w, n, m: suffix_array.contains(
            suffix_array.prefix_doubling(t, n), t, w, n, m),
    ],
    [ 'lcp-lr array', lcp_lr_contains ],
]

class TestExactStringMatching(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_first_exact_match(self, t, w, n, m, reference, algorithm):
    self.assertEqual(next(algorithm(t, w, n, m)), reference)

  def check_all_exact_matches(self, t, w, n, m, reference, algorithm):
    self.assertEqual(list(algorithm(t, w, n, m)), reference)

  def check_no_match(self, t, w, n, m, algorithm):
    self.assertFalse(list(algorithm(t, w, n, m)))

  @parameterized.parameterized.expand(EXACT_STRING_MATCHING_ALGORITHMS)
  def test_example_first_exact_match(self, _, algorithm):
    self.check_first_exact_match('#abaaba', '#aab', 6, 3, 3, algorithm)
    self.check_first_exact_match('#abrakadabra', '#brak', 11, 4, 2, algorithm)
    self.check_first_exact_match('#abrakadabra', '#ra', 11, 2, 3, algorithm)

  @parameterized.parameterized.expand(EXACT_STRING_MATCHING_ALGORITHMS)
  def test_example_all_exact_matches(self, _, algorithm):
    self.check_all_exact_matches(
        '#abaaabbaababb', '#abb', 13, 3, [5, 11], algorithm)
    self.check_all_exact_matches(
        '#abrakadabra', '#a', 11, 1, [1, 4, 6, 8, 11], algorithm)
    self.check_all_exact_matches(
        '#abrakadabra', '#bra', 11, 3, [2, 9], algorithm)
    self.check_all_exact_matches('#abrakadabra', '#rak', 11, 3, [3], algorithm)

  @parameterized.parameterized.expand(EXACT_STRING_MATCHING_ALGORITHMS)
  def test_example_no_match(self, _, algorithm):
    self.check_no_match('#abaaba', '#baaab', 6, 5, algorithm)
    self.check_no_match('#abrakadabra', '#l', 11, 1, algorithm)
    self.check_no_match('#abrakadabra', '#xyz', 11, 3, algorithm)

  @parameterized.parameterized.expand(EXACT_STRING_MATCHING_ALGORITHMS)
  @run_large
  def test_random_exact_string_matching(self, _, algorithm):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A)
      reference = list(forward.brute_force(t, w, n, m))
      self.check_all_exact_matches(t, w, n, m, reference, algorithm)

  @parameterized.parameterized.expand(EXACT_STRING_MATCHING_ALGORITHMS)
  @run_large
  def test_all_exact_string_matching(self, _, algorithm):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for t in itertools.product(A, repeat = n):
          t = '#' + ''.join(t)
          for w in itertools.product(A, repeat = m):
            w = '#' + ''.join(w)
            reference = list(forward.brute_force(t, w, n, m))
            self.check_all_exact_matches(t, w, n, m, reference, algorithm)
