import unittest

from approximate_string_matching import distance, lcs

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
  def check_lcs(self, t_1, t_2, n_1, n_2, reference):
    self.assertEqual(lcs.needleman_wunsch(t_1, t_2, n_1, n_2), reference)

  def test_lcs(self):
    self.check_lcs('#COELACANTH', '#PELICAN', 10, 7, ('ELCAN', 7))
    self.check_lcs(
        '#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17,
        ('TGCCGCGCAAAACAGC', 3))
