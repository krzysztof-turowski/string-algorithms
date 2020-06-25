import os
import unittest

from approximate_string_matching import linear_space_lcs, lcs
from generator import rand

LCS_ALGORITHMS = [
    linear_space_lcs.linear_space_lcs,
]

class TestLinearSpaceLongestCommonSubsequence(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  """Test if substr is subsequence of the word"""
  def is_subsequence(self, word, substr):
    j = 0
    for i in range(0, len(word)):
      if word[i] == substr[j]:
        j = j + 1
      if j == len(substr):
        return True

    return False

  """Check if lcs length equal to returned by needleman_wunsch algorithm
      and if lcs is substring of both word given as arguments"""
  def check_linear_space_lcs(self, t_1, t_2, n_1, n_2):
    lcs_word = lcs.needleman_wunsch(t_1, t_2, n_1 - 1, n_2 - 1)
    exact_length = len(lcs_word[0]) + 1

    for algorithm in LCS_ALGORITHMS:
      lcs_word, lcs_length = algorithm(t_1, t_2, n_1, n_2)

      self.assertEqual(lcs_length,
                       exact_length,
                       'Wrong lcs length: {} != {}'.format(exact_length,
                                                           lcs_length)
                       )

      self.assertTrue(self.is_subsequence(t_1, lcs_word),
                      'Word {} does not contain {}'.format(t_1, lcs_word)
                      )
      self.assertTrue(self.is_subsequence(t_2, lcs_word),
                      'Word {} does not contain {}'.format(t_2, lcs_word)
                      )

  def test__linear_space_lcs(self):
    self.check_linear_space_lcs('aab', 'baa', 3, 3)
    self.check_linear_space_lcs('COELACANTH', 'PELICAN', 10, 7)
    self.check_linear_space_lcs('TGGCCGCGCAAAAACAGC',
                                'TGACCGCGCAAAACAGC',
                                18, 17,)

  @run_large
  def test_random_string_lcs(self):
    T, n_1, n_2, A = 100, 100, 50, ['a', 'b']
    for _ in range(T):
      t_1, t_2 = rand.random_word(n_1, A), rand.random_word(n_2, A)
      self.check_linear_space_lcs(t_1, t_2, len(t_1), len(t_2))
