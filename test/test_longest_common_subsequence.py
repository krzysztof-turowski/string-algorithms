import itertools
import os
import unittest

import parameterized

from approximate_string_matching import distance, lcs, four_russians
from generator import rand

LCS_ALGORITHMS = [
    [ 'Needleman-Wunsch', lcs.needleman_wunsch ],
    [ 'Hirschberg', lcs.hirschberg ],
    [ 'Kumar-Rangan', lcs.kumar_rangan ],
    [ 'Myers', lcs.myers],
    [ 'four Russians', four_russians.four_russians_lcs ],
]
FOUR_RUSSIANS = [ 'four Russians', four_russians.four_russians_lcs ]

def is_subsequence(t, w):
  it = iter(t)
  return all(any(ci == cj for ci in it) for cj in w)

class TestLongestCommonSubsequence(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_lcs(self, t_1, t_2, n_1, n_2, d, algorithm):
    result = algorithm(t_1, t_2, n_1, n_2, distance.INDEL_DISTANCE)
    self.assertTrue(is_subsequence(t_1, result))
    self.assertTrue(is_subsequence(t_2, result))
    self.assertEqual(len(result), (n_1 + n_2 - d) // 2)

  @parameterized.parameterized.expand(LCS_ALGORITHMS)
  def test_examples(self, _, algorithm):
    self.check_lcs('#aab', '#baa', 3, 3, 2, algorithm)
    self.check_lcs('#aabaa', '#abaab', 5, 5, 2, algorithm)
    self.check_lcs('#baabab', '#ababaa', 6, 6, 4, algorithm)
    self.check_lcs('#aab', '#baa', 3, 3, 2, algorithm)
    self.check_lcs('#', '#', 0, 0, 0, algorithm)
    self.check_lcs('#aaa', '#', 3, 0, 3, algorithm)
    self.check_lcs('#aaa', '#aaa', 3, 3, 0, algorithm)
    self.check_lcs('#aaab', '#baaa', 4, 4, 2, algorithm)
    self.check_lcs('#baaba', '#babaa', 5, 5, 2, algorithm)
    self.check_lcs('#baaa', '#ababaa', 4, 6, 2, algorithm)

  @parameterized.parameterized.expand(
      algorithm for algorithm in LCS_ALGORITHMS if algorithm != FOUR_RUSSIANS)
  @run_large
  def test_examples_long(self, _, algorithm):
    self.check_lcs('#COELACANTH', '#PELICAN', 10, 7, 7, algorithm)
    self.check_lcs(
        '#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17, 3, algorithm)

  @parameterized.parameterized.expand(LCS_ALGORITHMS)
  @run_large
  def test_random_lcs(self, _, algorithm):
    T, n_1, n_2, A = 100, 7, 7, ['a', 'b']
    for _ in range(T):
      t_1, t_2 = rand.random_word(n_1, A), rand.random_word(n_2, A)
      self.check_lcs(
          t_1, t_2, n_1, n_2,
          distance.distance(t_1, t_2, n_1, n_2, distance.INDEL_DISTANCE),
          algorithm)

  @parameterized.parameterized.expand(LCS_ALGORITHMS)
  @run_large
  def test_all_lcs(self, _, algorithm):
    N_1, N_2, A = 4, 4, ['a', 'b']
    for n_1 in range(2, N_1 + 1):
      for t_1 in itertools.product(A, repeat = n_1):
        t_1 = '#' + ''.join(t_1)
        for n_2 in range(2, N_2 + 1):
          for t_2 in itertools.product(A, repeat = n_2):
            t_2 = '#' + ''.join(t_2)
            self.check_lcs(
                t_1, t_2, n_1, n_2,
                distance.distance(t_1, t_2, n_1, n_2, distance.INDEL_DISTANCE),
                algorithm)
