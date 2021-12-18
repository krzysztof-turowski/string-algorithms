import math
import os
import random
import unittest

import parameterized

from generator import rand
from shortest_common_superstring import shortest_common_superstring

SHORTEST_COMMON_SUPERSTRING_ALGORITHMS = [
    [
        'group_merge',
        shortest_common_superstring.group_merge,
        lambda n: 2 * math.ceil(math.log(n) + 1) * n
    ],
    [
        'mgreedy',
        shortest_common_superstring.mgreedy,
        lambda n: 3 * n,
    ],
    [
        'tgreedy',
        shortest_common_superstring.tgreedy,
        lambda n: 4 * n,
    ],
    [
        'greedy',
        shortest_common_superstring.greedy,
        lambda n: 2 * n,
    ]
]

class TestShortestCommonSuperstring(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_shortest_common_superstring(self, W, reference, algorithm, bound):
    result = algorithm(W)
    self.assertTrue(
        all(word[1:] in result for word in W),
        f'Algorithm {algorithm.__name__}, words {W}')
    if reference is not None:
      self.assertTrue(len(result) - 1 <= bound(len(reference) - 1))

  @parameterized.parameterized.expand(SHORTEST_COMMON_SUPERSTRING_ALGORITHMS)
  def test_examples(self, _, algorithm, bound):
    self.check_shortest_common_superstring(
        ['#abc'], '#abc', algorithm, bound)
    self.check_shortest_common_superstring(
        ['#abc', '#ab', '#c'], '#abc', algorithm, bound)
    self.check_shortest_common_superstring(
        ['#a', '#b', '#c', '#d', '#e', '#f', '#g'], '#abcdefg',
        algorithm, bound)
    self.check_shortest_common_superstring(
        ['#abc', '#bca', '#cab', '#d'], '#abcabd', algorithm, bound)

  @parameterized.parameterized.expand(SHORTEST_COMMON_SUPERSTRING_ALGORITHMS)
  @run_large
  def test_small_words(self, _, algorithm, bound):
    tests, k, n_low, n_high, A = 100, 10, 1, 3, ['a', 'b', 'c']
    for _ in range(tests):
      T = [rand.random_word(random.randint(n_low, n_high), A)
           for _ in range(k)]
      self.check_shortest_common_superstring(
          T, shortest_common_superstring.exact(T), algorithm, bound)

  @parameterized.parameterized.expand(SHORTEST_COMMON_SUPERSTRING_ALGORITHMS)
  @run_large
  def test_random(self, _, algorithm, bound):
    tests, k, n_low, n_high, A = 100, 10, 20, 50, ['a', 'b', 'c', 'd']
    for _ in range(tests):
      T = [rand.random_word(random.randint(n_low, n_high), A)
           for _ in range(k)]
      self.check_shortest_common_superstring(T, None, algorithm, bound)

  @run_large
  @parameterized.parameterized.expand(SHORTEST_COMMON_SUPERSTRING_ALGORITHMS)
  def test_strict_bound_for_group_merge(self, _, algorithm, bound):
    def get_si(i, k):
      return ['#' + ('a' * j) + ('b' * ((4 ** k) - j))
              for j in range(4 ** (k - i) // 2, 4 ** (k - i) + 1)]
    k = 2
    S = [S_i for i in range(k) for S_i in get_si(i, k)]
    V = ['#' + 'c' + ('b' * (i - 1)) + 'c' + ('a' * (4 ** i - i - 1))
         for i in range(1, k + 1)]
    # TODO: fix
    reference = None
    self.check_shortest_common_superstring(S + V, reference, algorithm, bound)
