import itertools
import os
import unittest

from generator import rand
from approximate_string_matching import dont_care, matching_with_dont_cares

class TestExactMatchingWithDontCaresCase(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def make_test(self, text, pattern, result):
    matches = matching_with_dont_cares.exact_matching_with_dont_cares(
        text, pattern, len(text), len(pattern))
    self.assertEqual(result, list(matches))

  def test_given_input_with_no_wildcards_returns_matches(self):
    self.make_test('#abbabaaa', '#ab', [1, 4])

  def test_given_input_with_wildcards_returns_matches(self):
    self.make_test('#abbabaaa', '#??a', [2, 4, 5, 6])

  def test_simple(self):
    self.make_test('#aa', '#a', [1, 2])

  @run_large
  def test_random_exact_string_matching(self):
    T, n, m, A = 100, 500, 10, ['a', 'b']
    for _ in range(T):
      t, w = rand.random_word(n, A), rand.random_word(m, A + ['?'])
      reference = list(dont_care.basic_fft(t, w, n, m))
      self.make_test(t, w, reference)

  @run_large
  def test_all_exact_string_matching(self):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for t in itertools.product(A, repeat = n):
          t = '#' + ''.join(t)
          for w in itertools.product(A + ['?'], repeat = m):
            w = '#' + ''.join(w)
            reference = list(dont_care.basic_fft(t, w, n, m))
            self.make_test(t, w, reference)
