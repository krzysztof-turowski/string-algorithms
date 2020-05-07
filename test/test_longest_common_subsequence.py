import itertools
import os
import unittest

from approximate_string_matching import distance, lcs
from generator import rand

LCS_ALGORITHMS = [
    lcs.needleman_wunsch,
    lcs.hirschberg,
]

class TestStringDistance(unittest.TestCase):
  def check_hamming_distance(self, t_1, t_2, n_1, n_2, reference):
    self.assertEqual(n_1, n_2)
    self.assertEqual(distance.hamming_distance(t_1, t_2, n_1, n_2), reference)

  def check_edit_distance(self, t_1, t_2, n_1, n_2, reference):
    self.assertEqual(distance.edit_distance(t_1, t_2, n_1, n_2), reference)

  def test_hamming_distance(self):
    self.check_hamming_distance(
        '#GAGGTAGCGGCGTT', '#GTGGTAACGGGGTT', 14, 14, 3)

  def test_edit_distance(self):
    self.check_edit_distance(
        '#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17, 2)
    self.check_edit_distance(
        '#GCGTATGCGGCTAACGC', '#GCTATGCGGCTATACGC', 17, 17, 2)

class TestLongestCommonSubsequence(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_indel_distance(self, t_1, t_2, n_1, n_2, reference):
    for algorithm in LCS_ALGORITHMS:
      self.assertEqual(
          algorithm(t_1, t_2, n_1, n_2)[1],
          reference,
          'Algorithm {}, texts {}, {}'.format(algorithm.__name__, t_1, t_2))

  def check_lcs(self, t_1, t_2, n_1, n_2, reference):
    for algorithm in LCS_ALGORITHMS:
      self.assertEqual(
          algorithm(t_1, t_2, n_1, n_2),
          reference,
          'Algorithm {}, texts {}, {}'.format(algorithm.__name__, t_1, t_2))

  def test_lcs(self):
    self.check_lcs('#aab', '#baa', 3, 3, ('aa', 2))
    self.check_lcs('#COELACANTH', '#PELICAN', 10, 7, ('ELCAN', 7))
    self.check_lcs(
        '#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17,
        ('TGCCGCGCAAAACAGC', 3))

  @run_large
  def test_random_exact_string_matching(self):
    T, n_1, n_2, A = 100, 100, 50, ['a', 'b']
    for _ in range(T):
      t_1, t_2 = rand.random_word(n_1, A), rand.random_word(n_2, A)
      reference = lcs.needleman_wunsch(t_1, t_2, n_1, n_2)[1]
      self.check_indel_distance(t_1, t_2, n_1, n_2, reference)

  @run_large
  def test_all_exact_string_matching(self):
    N_1, N_2, A = 5, 5, ['a', 'b']
    for n_1 in range(3, N_1 + 1):
      for t_1 in itertools.product(A, repeat = n_1):
        t_1 = '#' + ''.join(t_1)
        for n_2 in range(3, N_2 + 1):
          for t_2 in itertools.product(A, repeat = n_2):
            t_2 = '#' + ''.join(t_2)
            reference = distance.indel_distance(t_1, t_2, n_1, n_2)
            self.check_indel_distance(t_1, t_2, n_1, n_2, reference)
