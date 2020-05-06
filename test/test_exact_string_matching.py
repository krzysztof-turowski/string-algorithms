import itertools
import os
import unittest

from common import prefix, suffix
from generator import rand
from exact_string_matching import forward, backward, other
from string_indexing import suffix_tree, suffix_array

EXACT_STRING_MATCHING_ALGORITHMS = [
    forward.morris_pratt,
    forward.knuth_morris_pratt,
    backward.boyer_moore,
    backward.boyer_moore_bad_shift,
    backward.bad_shift_heuristic,
    backward.boyer_moore_galil,
    backward.quick_search,
    backward.horspool,
    other.fast_on_average,
    other.two_way,
]

class TestPrefixSuffixArrays(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_prefix_suffix(self, t, n, reference):
    self.assertEqual(prefix.prefix_suffix(t, n), reference)
    self.assertEqual(prefix.prefix_suffix_from_strong_prefix_suffix(
        prefix.strong_prefix_suffix(t, n)), reference)

  def check_strong_prefix_suffix(self, t, n, reference):
    self.assertEqual(prefix.strong_prefix_suffix(t, n), reference)

  def check_prefix_prefix(self, t, n, reference):
    self.assertEqual(prefix.prefix_prefix_brute_force(t, n), reference)
    self.assertEqual(prefix.prefix_prefix(t, n), reference)

  def check_boyer_moore_shift(self, t, n, reference):
    self.assertEqual(suffix.boyer_moore_shift_brute_force(t, n), reference)
    self.assertEqual(suffix.boyer_moore_shift(t, n), reference)

  def test_prefix_suffix(self):
    self.check_prefix_suffix('#abaab', 5, [-1, 0, 0, 1, 1, 2])
    self.check_prefix_suffix(
        '#abababababb', 11, [-1, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0])

  def test_strong_prefix_suffix(self):
    self.check_strong_prefix_suffix('#abaab', 5, [-1, 0, -1, 1, 0, 2])
    self.check_strong_prefix_suffix(
        '#abaababa', 8, [-1, 0, -1, 1, 0, -1, 3, -1, 3])

  def test_prefix_prefix(self):
    self.check_prefix_prefix('#abaab', 5, [-1, 5, 0, 1, 2, 0])
    self.check_prefix_prefix('#aabbaaab', 8, [-1, 8, 1, 0, 0, 2, 3, 1, 0])
    self.check_prefix_prefix('#abaa', 4, [-1, 4, 0, 1, 1])
    self.check_prefix_prefix('#aabb', 4, [-1, 4, 1, 0, 0])

  def test_boyer_moore_shift(self):
    self.check_boyer_moore_shift('#abaaba', 6, [3, 3, 3, 3, 5, 2, 1])

  @run_large
  def test_random_boyer_moore_shift(self):
    T, n, A = 100, 100, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference_result = suffix.boyer_moore_shift_brute_force(t, n)
      self.check_boyer_moore_shift(t, n, reference_result)

  @run_large
  def test_all_boyer_moore_shift(self):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference_result = suffix.boyer_moore_shift_brute_force(t, n)
        self.check_boyer_moore_shift(t, n, reference_result)

class TestExactStringMatching(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_get_first_exact_match(self, t, w, n, m, reference):
    for algorithm in EXACT_STRING_MATCHING_ALGORITHMS:
      self.assertEqual(
          next(algorithm(t, w, n, m)),
          reference,
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))
    self.assertEqual(
        next(suffix_tree.contains(suffix_tree.naive(t, n), t, w, n, m)),
        reference,
        'Suffix tree, text {}, pattern {}'.format(t, w))
    self.assertEqual(
        next(suffix_array.contains(suffix_array.naive(t, n), t, w, n, m)),
        reference,
        'Suffix array, text {}, pattern {}'.format(t, w))

  def check_get_all_exact_matches(self, t, w, n, m, reference):
    for algorithm in EXACT_STRING_MATCHING_ALGORITHMS:
      self.assertEqual(
          list(algorithm(t, w, n, m)),
          reference,
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))
    self.assertEqual(
        list(suffix_tree.contains(suffix_tree.naive(t, n), t, w, n, m)),
        reference,
        'Suffix tree, text {}, pattern {}'.format(t, w))
    self.assertEqual(
        list(suffix_array.contains(suffix_array.naive(t, n), t, w, n, m)),
        reference,
        'Suffix array, text {}, pattern {}'.format(t, w))

  def check_no_match(self, t, w, n, m):
    for algorithm in EXACT_STRING_MATCHING_ALGORITHMS:
      self.assertFalse(
          list(algorithm(t, w, n, m)),
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))
    self.assertFalse(
        list(suffix_tree.contains(suffix_tree.naive(t, n), t, w, n, m)),
        'Suffix tree, text {}, pattern {}'.format(t, w))
    self.assertFalse(
        list(suffix_array.contains(suffix_array.naive(t, n), t, w, n, m)),
        'Suffix array, text {}, pattern {}'.format(t, w))

  def test_get_first_exact_match(self):
    self.check_get_first_exact_match('#abaaba', '#aab', 6, 3, 3)

  def test_get_all_exact_matches(self):
    self.check_get_all_exact_matches('#abaaabbaababb', '#abb', 13, 3, [5, 11])

  def test_no_match(self):
    self.check_no_match('#abaaba', '#baaab', 6, 5)

  @run_large
  def test_random_exact_string_matching(self):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A)
      reference = list(forward.brute_force(t, w, n, m))
      self.check_get_all_exact_matches(t, w, n, m, reference)

  @run_large
  def test_all_exact_string_matching(self):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for t in itertools.product(A, repeat = n):
          t = '#' + ''.join(t)
          for w in itertools.product(A, repeat = m):
            w = '#' + ''.join(w)
            reference = list(forward.brute_force(t, w, n, m))
            self.check_get_all_exact_matches(t, w, n, m, reference)
