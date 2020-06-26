import itertools
import os
import unittest

from generator import rand
from exact_string_matching import forward, backward, other
from string_indexing import suffix_tree, suffix_array

EXACT_STRING_MATCHING_ALGORITHMS = [
    forward.morris_pratt,
    forward.knuth_morris_pratt,
    forward.galil_seiferas,
    backward.boyer_moore,
    backward.boyer_moore_bad_shift,
    backward.bad_shift_heuristic,
    backward.boyer_moore_galil,
    backward.quick_search,
    backward.horspool,
    backward.boyer_moore_turbo,
    other.karp_rabin,
    other.fast_on_average,
    other.two_way,
]

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
