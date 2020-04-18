import unittest

from approximate_string_matching import distance

class TestStringDistance(unittest.TestCase):
  def check_hamming_distance(self, t, w, n, m, reference):
    self.assertEqual(n, m)
    self.assertEqual(distance.hamming_distance(t, w, n, m), reference)

  def check_edit_distance(self, t, w, n, m, reference):
    self.assertEqual(distance.edit_distance(t, w, n, m), reference)

  def test_hamming_distance(self):
    self.check_hamming_distance(
        '#GAGGTAGCGGCGTT', '#GTGGTAACGGGGTT', 14, 14, 3)

  def test_edit_distance(self):
    self.check_edit_distance(
        '#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17, 2)
    self.check_edit_distance(
        '#GCGTATGCGGCTAACGC', '#GCTATGCGGCTATACGC', 17, 17, 2)
