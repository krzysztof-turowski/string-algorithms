import itertools
import os
import random
import unittest

import parameterized

from approximate_string_matching import distance, matching_with_mismatches
from generator import rand

APPROXIMATE_STRING_MATCHING_HAMMING_ALGORITHMS = [
    [
        'naive Hamming',
        matching_with_mismatches.naive_hamming,
    ],
    [
        'Landau-Vishkin',
        matching_with_mismatches.landau_vishkin,
    ],
    [
        'Bitap-Shift-Add',
        matching_with_mismatches.bitap_shift_add,
    ],
    [   'grossi_luccio A3',
        matching_with_mismatches.grossi_luccio_a3,
    ],
    [
        'grossi_luccio A4',
        lambda t, w, n, m, k: matching_with_mismatches.grossi_luccio_a4(
            t, w, n, m, k, matching_with_mismatches.LcpLca),
    ],
]

APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS = [
    [
        'naive edit distance',
        matching_with_mismatches.naive_edit_distance,
    ],
    [
        'approximate Boyer-Moore',
        matching_with_mismatches.approximate_boyer_moore,
    ],
]

class TestApproximateStringMatching(unittest.TestCase):
  def check_get_first_match(
      self, t, w, n, m, k, reference, algorithm):
    self.assertEqual(
        next(algorithm(t, w, n, m, k)),
        reference,
        f'Algorithm {algorithm.__name__}, text {t}, pattern {w}')

  def check_get_all_matches(
      self, t, w, n, m, k, reference, algorithm):
    self.assertEqual(
        sorted(list(algorithm(t, w, n, m, k))),
        reference,
        f'Algorithm {algorithm.__name__}, text {t}, pattern {w}')

  def check_no_match(self, t, w, n, m, k, algorithm):
    self.assertFalse(
        list(algorithm(t, w, n, m, k)),
        f'Algorithm {algorithm.__name__}, text {t}, pattern {w}')

class TestApproximateStringMatchingWithHammingDistance(
    TestApproximateStringMatching):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  @staticmethod
  def check_hamming_distance(t, w, m, k, index):
    if index + m > len(t):
      return False
    return distance.distance(
        '#' + t[index:index + m], w, m, m, distance.HAMMING_DISTANCE) <= k

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_HAMMING_ALGORITHMS)
  def test_get_first_match(self, _, algorithm):
    self.check_get_first_match('#bbbbaaa', '#aab', 7, 3, 1, 5, algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_HAMMING_ALGORITHMS)
  def test_get_all_matches(self, _, algorithm):
    self.check_get_all_matches('#bbbbaaab', '#aab', 8, 3, 1, [5, 6], algorithm)
    self.check_get_all_matches('#abbaba', '#?ba', 6, 3, 1, [2, 4], algorithm)
    self.check_get_all_matches(
        '#abbab', '#?ba', 5, 3, 3, [1, 2, 3], algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_HAMMING_ALGORITHMS)
  @run_large
  def test_random_string_matching(self, _, algorithm):
    T, n, m, K, A = 100, 20, 10, 6, ['a', 'b']
    for _ in range(T):
      for k in range(1, K + 1):
        t, w = rand.random_word(n, A), rand.random_word(m, A)
        reference = [index for index in range(1, n + 1)
                     if self.check_hamming_distance(t, w, m, k, index)]
        self.check_get_all_matches(t, w, n, m, k, reference, algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_HAMMING_ALGORITHMS)
  @run_large
  def test_all_string_matching(self, _, algorithm):
    N, M, K, A = 7, 3, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for k in range(1, K + 1):
          for t in itertools.product(A, repeat = n):
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
      APPROXIMATE_STRING_MATCHING_HAMMING_ALGORITHMS)
  @run_large
  def test_random_string_matching_with_mismatches(self, _, algorithm):
    T, n, m, k, A = 100, 50, 10, 4, ['a', 'b']
    for _ in range(T):
      t, w = self.generate(n, m, k, A)
      reference = [index for index in range(1, n + 1)
                   if self.check_hamming_distance(t, w, m, k, index)]
      self.check_get_all_matches(t, w, n, m, k, reference, algorithm)

class TestApproximateStringMatchingWithEditDistance(
    TestApproximateStringMatching):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  @staticmethod
  def check_edit_distance(t, w, m, k, index):
    for i in range(max(0, index - m - k), index):
      if distance.distance(
          '#' + t[i + 1:index + 1], w, index - i, m,
          distance.EDIT_DISTANCE) <= k:
        return True
    return False

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS)
  def test_get_first_match(self, _, algorithm):
    self.check_get_first_match('#abbaba', '#?ba', 6, 3, 1, 4, algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS)
  def test_get_all_matches(self, _, algorithm):
    self.check_get_all_matches(
        '#abaaabbaababb', '#a?b', 13, 3, 1, [2, 6, 7, 10, 12, 13], algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS)
  def test_no_match(self, _, algorithm):
    self.check_no_match('#abaaba', '#b?b?b', 6, 5, 2, algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS)
  @run_large
  def test_random_string_matching(self, _, algorithm):
    T, n, m, K, A = 100, 20, 10, 6, ['a', 'b']
    for _ in range(T):
      for k in range(1, K + 1):
        t, w = rand.random_word(n, A), rand.random_word(m, A)
        reference = [index for index in range(1, n + 1)
                     if self.check_edit_distance(t, w, m, k, index)]
        self.check_get_all_matches(t, w, n, m, k, reference, algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS)
  @run_large
  def test_all_string_matching_with_dont_care(self, _, algorithm):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        for m in range(1, M + 1):
          for w in itertools.product(A + ['?'], repeat = m):
            w = '#' + ''.join(w)
            k = w.count('?')
            reference = [index for index in range(1, n + 1)
                         if self.check_edit_distance(t, w, m, k, index)]
            self.check_get_all_matches(t, w, n, m, k, reference, algorithm)

  @parameterized.parameterized.expand(
      APPROXIMATE_STRING_MATCHING_EDIT_ALGORITHMS)
  @run_large
  def test_all_string_matching(self, _, algorithm):
    N, M, K, A = 7, 3, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for k in range(1, K + 1):
          for t in itertools.product(A, repeat = n):
            t = '#' + ''.join(t)
            for w in itertools.product(A, repeat = m):
              w = '#' + ''.join(w)
              reference = [index for index in range(1, n + 1)
                           if self.check_edit_distance(t, w, m, k, index)]
              self.check_get_all_matches(t, w, n, m, k, reference, algorithm)
