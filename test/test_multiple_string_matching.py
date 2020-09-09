import unittest
import random
import os

import parameterized

from multiple_string_matching import multiple_string_matching
from exact_string_matching import forward
from generator.rand import random_word

MULTIPLE_STRING_MATCHING_ALGORITHMS = [
    [
        'Aho-Corasick',
        multiple_string_matching.aho_corasick_build,
        multiple_string_matching.aho_corasick_search,
    ],
    [
        'Commentz-Walter',
        multiple_string_matching.commentz_walter_build,
        multiple_string_matching.commentz_walter_search,
    ],
    [
        'fast practical multiple string matching',
        multiple_string_matching.fast_practical_multi_string_matching_build,
        multiple_string_matching.fast_practical_multi_string_matching_search,
    ],
]

class TestMultipleStringMatching(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_all_matches(self, t, n, W, reference, build, algorithm):
    self.assertSetEqual(
        set(algorithm(t, n, build(W))),
        set(reference),
        'Algorithm {}, text {}, patterns {}'.format(algorithm.__name__, t, W))

  def check_no_match(self, t, n, W, build, algorithm):
    self.assertFalse(
        list(algorithm(t, n, build(W))),
        'Algorithm {}, text {}, patterns {}'.format(algorithm.__name__, t, W))

  @parameterized.parameterized.expand(MULTIPLE_STRING_MATCHING_ALGORITHMS)
  def test_examples_all_matches(self, _, build, algorithm):
    self.check_all_matches(
        '#aabccabcab', 10, ['#abc'],
        {('abc', 2), ('abc', 6)},
        build, algorithm)
    self.check_all_matches(
        '#aabccabcab', 10, ['#aa', '#bcc', '#bcab'],
        {('aa', 1), ('bcc', 3), ('bcab', 7)},
        build, algorithm)
    self.check_all_matches(
        '#eshers', 6, ['#he', '#she', '#his', '#her', '#hers'],
        {('she', 2), ('he', 3), ('her', 3), ('hers', 3)},
        build, algorithm)
    self.check_all_matches(
        '#dacbaababababa', 14, ['#cacbaa', '#acb', '#aba', '#acbab', '#ccbab'],
        {('acb', 2), ('aba', 6), ('aba', 8), ('aba', 10), ('aba', 12)},
        build, algorithm)
    self.check_all_matches(
        '#abaabbacca', 10, ['#aba', '#cbbaa', '#cca', '#aabc', '#ab'],
        {('ab', 1), ('aba', 1), ('cca', 8), ('ab', 4)},
        build, algorithm)
    self.check_all_matches(
        '#bcbbcbacac', 10, ['#ccca', '#cac', '#bbac', '#bbcac'],
        {('cac', 8)},
        build, algorithm)

  @parameterized.parameterized.expand(MULTIPLE_STRING_MATCHING_ALGORITHMS)
  def test_examples_no_match(self, _, build, algorithm):
    self.check_no_match('#abababab', 8, ['#bb', '#abba'], build, algorithm)

  @parameterized.parameterized.expand(MULTIPLE_STRING_MATCHING_ALGORITHMS)
  def test_pessimistic(self, _, build, algorithm):
    t, n, W = '#' + 'a' * 20, 20, ['#' + i * 'a' for i in range(1, 6)]
    reference = {(w[1:], i) for w in W for i in range(1, n + 3 - len(w))}
    self.check_all_matches(t, n, W, reference, build, algorithm)

  @parameterized.parameterized.expand(MULTIPLE_STRING_MATCHING_ALGORITHMS)
  @run_large
  def test_random_small(self, _, build, algorithm):
    T, n, m, A = 100, 10, 5, ['a', 'b', 'c']
    for _ in range(T):
      t = random_word(n, A)
      W = {random_word(random.randint(2, 5), A) for _ in range(m)}
      reference = [(w[1:], i) for w in W
                   for i in forward.brute_force(t, w, n, len(w) - 1)]
      self.check_all_matches(t, n, W, reference, build, algorithm)

  @parameterized.parameterized.expand(MULTIPLE_STRING_MATCHING_ALGORITHMS)
  @run_large
  def test_random_big(self, _, build, algorithm):
    T, n, m, A = 100, 1000, 100, ['a', 'b', 'c']
    for _ in range(T):
      t = random_word(n, A)
      W = {random_word(random.randint(2, 5), A) for _ in range(m)}
      reference = [(w[1:], i) for w in W
                   for i in forward.brute_force(t, w, n, len(w) - 1)]
      self.check_all_matches(t, n, W, reference, build, algorithm)
