import itertools
import os
import random
import unittest

from random import randrange
import regex

from approximate_string_matching import dont_care, matching_with_dont_cares, \
  approximate_boyer_moore, distance
from approximate_string_matching.mismatches import string_matching_with_mismatches, brute_search
from generator import rand

STRING_MATCHING_WITH_DONT_CARE_ALGORITHMS = [
    dont_care.basic_fft,
    matching_with_dont_cares.exact_matching_with_dont_cares,
    matching_with_dont_cares.exact_matching_with_dont_cares_n_log_m
]

STRING_MATCHING_WITH_EDIT_DISTANCE_ALGORITHMS = [
    approximate_boyer_moore.approximate_boyer_moore,
    approximate_boyer_moore.simple_dynamic_edit_distance
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

class TestStringMatchingKMismatches(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_get_first_match(self):
    self.assertEqual([4],
                     list(string_matching_with_mismatches('bbbbaaa',
                                                          'aab', 6, 3, 1)))

  def test_get_all_matches(self):
    self.assertEqual([4, 5],
                     list(string_matching_with_mismatches('bbbbaaab',
                                                          'aab', 6, 3, 1)))

  def test_no_match(self):
    self.assertFalse(
        list(string_matching_with_mismatches('bbbbba',
                                             'aab', 6, 3, 1)))

  @run_large
  def test_random_string_matching_with_mismatches(self):
    T, n, m, k, A = 100, 50, 10, 4, ['a', 'b']
    for _ in range(T):
      t, w = gen_text(n, m, k, A)
      reference = brute_search(t, w, n, m, k)
      self.assertEqual(reference,
                       list(string_matching_with_mismatches(t, w, n, m, k)))

  @run_large
  def test_all_string_matching_with_mismatches(self):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for m in range(1, M + 1):
        for k in range(1, 3):
          for t in itertools.product(A, repeat = n):
            t = ''.join(t)
            for w in itertools.product(A, repeat = m):
              w = ''.join(w)
              reference = brute_search(t, w, n, m, k)
              self.assertEqual(
                  reference,
                  list(string_matching_with_mismatches(t, w, n, m, k)))


def gen_text(n:int, m:int, k: int, letters='abc'):
  text_res = ""
  if n <= m:
    n=m+1
  for _ in range(n):
    text_res += random.choice(letters)
  pos = random.randint(0, n-m)
  pat_res = text_res[pos:pos+m]
  for _ in range(k-1):
    x = random.randint(0, m)
    pat_res = pat_res[:x] + random.choice(letters) + pat_res[x+1:]
  return text_res[:n], pat_res[:m]

class TestStringMatchingWithEditDistance(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_get_first_match_with_edit_distance(self, t, w, n, m, k, reference):
    for algorithm in STRING_MATCHING_WITH_EDIT_DISTANCE_ALGORITHMS:
      self.assertEqual(
          next(algorithm(t, w, n, m, k)),
          reference,
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))

  def check_get_all_matches_with_edit_distance(self, t, w, n, m, k, reference):
    for algorithm in STRING_MATCHING_WITH_EDIT_DISTANCE_ALGORITHMS:
      self.assertEqual(
          list(algorithm(t, w, n, m, k)),
          reference,
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))

  def check_no_match(self, t, w, n, m, k):
    for algorithm in STRING_MATCHING_WITH_EDIT_DISTANCE_ALGORITHMS:
      self.assertFalse(
          list(algorithm(t, w, n, m, k)),
          'Algorithm {}, text {}, pattern {}'.format(
              algorithm.__name__, t, w))

  def test_get_first_match_with_dont_care(self):
    self.check_get_first_match_with_edit_distance('#abbaba', '#?ba', 6, 3, 1, 4)

  def test_get_all_matches_with_dont_care(self):
    self.check_get_all_matches_with_edit_distance(
        '#abaaabbaababb', '#a?b', 13, 3, 1, [2, 6, 7, 10, 12, 13])

  def test_no_match(self):
    self.check_no_match('#abaaba', '#b?b?b', 6, 5, 2)

  @run_large
  def test_random_string_matching_with_edit_distance(self):
    T, n, m, A = 100, 300, 10, ['a', 'b']
    for _ in range(T):
      t, w, k = rand.random_word(n, A), rand.random_word(m, A), randrange(m-1)
      reference = [index-1 for index in range(1, n+2)
                   if check_subwords(t, w, m, k, index)]
      self.check_get_all_matches_with_edit_distance(t, w, n, m, k, reference)

  @run_large
  def test_all_string_matching_with_dont_care(self):
    N, M, A = 7, 3, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        for m in range(1, M + 1):
          for w in itertools.product(A + ['?'], repeat = m):
            w = '#' + ''.join(w)
            k = w.count('?')
            reference = [index-1 for index in range(2, n+2)
                         if check_subwords(t, w, m, k, index)]
            self.check_get_all_matches_with_edit_distance(t, w, n, m, k,
                                                          reference)


def check_subwords(t, w, m, k, index):
  for i in range(max(1, index-m-k), index):
    if distance.edit_distance('#' + t[i:index], w, len(t[i:index]), m) <= k:
      return True

  return False
