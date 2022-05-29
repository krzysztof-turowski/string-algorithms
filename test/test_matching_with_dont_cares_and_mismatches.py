import itertools
import os
import random
import unittest

import parameterized

from approximate_string_matching import distance
from approximate_string_matching import matching_with_dont_cares_and_mismatches

MATCHING_WITH_DONT_CARES_AND_MISMATCHES_ALGORITHMS = [
    [
        'naive Hamming',
        matching_with_dont_cares_and_mismatches.naive_hamming_with_mismatches,
    ],
    [
        'nonrecursive randomised',
        matching_with_dont_cares_and_mismatches.nonrecursive_randomised
    ],
    [
        'recursive',
        matching_with_dont_cares_and_mismatches.recursive
    ],
    [
        'nonrecursive deterministic',
        matching_with_dont_cares_and_mismatches.nonrecursive_deterministic
    ],
]

class TestMatchingWithDontCaresAndMismatches(unittest.TestCase):
  def check_get_first_match(
      self, t, w, n, m, k, reference, algorithm):
    self.assertEqual(
        next(algorithm(t, w, n, m, k)),
        reference,
        f'Algorithm {algorithm.__name__}, text {t}, pattern {w}')

  def check_get_all_matches(
      self, t, w, n, m, k, reference, algorithm):
    self.assertEqual(
        list(algorithm(t, w, n, m, k)),
        reference,
        f'Algorithm {algorithm.__name__}, text {t}, pattern {w}')

  def check_no_match(self, t, w, n, m, k, algorithm):
    self.assertFalse(
        list(algorithm(t, w, n, m, k)),
        f'Algorithm {algorithm.__name__}, text {t}, pattern {w}')

class TestMatchingWithDontCaresAndMismatchesWithHammingDistance(
    TestMatchingWithDontCaresAndMismatches):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  @staticmethod
  def check_hamming_distance(t, w, m, k, index):
    if index + m > len(t):
      return False
    return distance.hamming_distance(
        '#' + t[index:index + m], w, m, m, wildcard_symbol='?') <= k

  @parameterized.parameterized.expand(
      MATCHING_WITH_DONT_CARES_AND_MISMATCHES_ALGORITHMS)
  def test_get_first_match(self, _, algorithm):
    self.check_get_first_match('#bbcbaaa?', '#a?b', 8, 3, 1, 2, algorithm)

  @parameterized.parameterized.expand(
      MATCHING_WITH_DONT_CARES_AND_MISMATCHES_ALGORITHMS)
  def test_get_all_matches(self, _, algorithm):
    self.check_get_all_matches(
      '#bbbbaaa?', '#a?b', 8, 3, 1, [1,2, 5, 6], algorithm
    )
    self.check_get_all_matches(
      '#ababba?aba??aba', '#abcc?aa', 15, 7, 2, [1, 6, 8], algorithm
    )

  @parameterized.parameterized.expand(
      MATCHING_WITH_DONT_CARES_AND_MISMATCHES_ALGORITHMS)
  @run_large
  def test_all_string_matching(self, _, algorithm):
    N, M, K, A = 4, 3, 1, ['a', 'b','?']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for k in range(1, K + 1):
          for t in itertools.product(A, repeat = n):
            if sum(c == '?' for c in t) > 1:
              continue
            t = '#' + ''.join(t)
            for w in itertools.product(A, repeat = m):
              w = '#' + ''.join(w)
              reference = [index for index in range(1, n + 1)
                           if self.check_hamming_distance(t, w, m, k, index)]
              self.check_get_all_matches(t, w, n, m, k, reference, algorithm)

  @staticmethod
  def generate(n, m, k, A):
    text = ''.join(random.choice(A) for _ in range(n))
    index = random.randint(0, n - m)
    word = text[index:index + m]
    for _ in range(k - 1):
      x = random.randint(0, m)
      word = word[:x] + random.choice(A) + word[x + 1:]
    return '#' + text[:n], '#' + word[:m]

  @parameterized.parameterized.expand(
      MATCHING_WITH_DONT_CARES_AND_MISMATCHES_ALGORITHMS)
  @run_large
  def test_random_string_matching_with_mismatches(self, _, algorithm):
    T, n, m, k, A = 100, 200, 20, 6, ['a', 'a', 'b', 'b', '?']
    for _ in range(T):
      t, w = self.generate(n, m, k, A)
      reference = [index for index in range(1, n + 1)
                   if self.check_hamming_distance(t, w, m, k, index)]
      self.check_get_all_matches(t, w, n, m, k, reference, algorithm)
