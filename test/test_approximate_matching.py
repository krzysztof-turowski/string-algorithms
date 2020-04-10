import unittest

class TestStringDistance(unittest.TestCase):
  def test_hamming_distance(self, t, w, n, m, reference):
    self.assertEqual(n, m)
    self.assertEqual(
        approximate_matching.hamming_distance(t, w, n, m), reference)

  def test_edit_distance(self, t, w, n, m, reference):
    self.assertEqual(
        approximate_matching.edit_distance(t, w, n, m), reference)

test = TestStringDistance()
test.test_hamming_distance('#GAGGTAGCGGCGTT', '#GTGGTAACGGGGTT', 14, 14, 3)

test.test_edit_distance('#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17, 2)
test.test_edit_distance('#GCGTATGCGGCTAACGC', '#GCTATGCGGCTATACGC', 17, 17, 2)
