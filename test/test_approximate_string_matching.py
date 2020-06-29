import itertools
import os
import unittest

import regex

from approximate_string_matching import dont_care
from generator import rand

STRING_MATCHING_WITH_DONT_CARE_ALGORITHMS = [
    dont_care.basic_fft,
]

class TestStringMatchingWithDontCare(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_get_first_match_with_dont_care(self, t, w, n, m, reference):
    for algorithm in STRING_MATCHING_WITH_DONT_CARE_ALGORITHMS:
      self.assertEqual(
          reference,
          next(algorithm(t, w, n, m)),
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))

  def check_get_all_matches_with_dont_care(self, t, w, n, m, reference):
    for algorithm in STRING_MATCHING_WITH_DONT_CARE_ALGORITHMS:
      self.assertEqual(
          reference,
          list(algorithm(t, w, n, m)),
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))

  def check_no_match(self, t, w, n, m):
    for algorithm in STRING_MATCHING_WITH_DONT_CARE_ALGORITHMS:
      self.assertFalse(
          list(algorithm(t, w, n, m)),
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))

  def test_get_first_match_with_dont_care(self):
    self.check_get_first_match_with_dont_care('#abbaba', '#?ba', 6, 3, 2)

  def test_get_all_matches_with_dont_care(self):
    self.check_get_all_matches_with_dont_care(
        '#abaaabbaababb', '#a?b', 13, 3, [4, 5, 8, 11])

  def test_no_match(self):
    self.check_no_match('#abaaba', '#b???b', 6, 5)

  @run_large
  def test_random_string_matching_with_dont_care(self):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A)
      reference = [match.start() + 1 for match in regex.finditer(
          w[1:].replace('?', '.'), t[1:], overlapped = True)]
      self.check_get_all_matches_with_dont_care(t, w, n, m, reference)

  @run_large
  def test_all_string_matching_with_dont_care(self):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        for m in range(1, M + 1):
          for w in itertools.product(A + ['?'], repeat = m):
            w = '#' + ''.join(w)
            reference = [match.start() + 1 for match in regex.finditer(
                w[1:].replace('?', '.'), t[1:], overlapped = True)]
            self.check_get_all_matches_with_dont_care(t, w, n, m, reference)
