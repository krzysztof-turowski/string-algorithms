import unittest

from string_indexing import farach_suffix_tree


# small tests used to debug program
class TestSuffixArrays(unittest.TestCase):
  def test_example(self):
    text = [1, 2, 1, 1, 1, 2, 2, 1, 2, 2, 2, 1]
    T, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(text)
    self.assertEqual(A_T, [12, 3, 4, 1, 5, 8, 11, 2, 7, 10, 6, 9])
    self.assertEqual(LCP_T, [1, 2, 1, 2, 3, 0, 2, 2, 1, 3, 2])

  def test_suffix_array_small(self):
    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree([1, 2, 1, 1, 2, 1])
    self.assertEqual(A_T, [6, 3, 4, 1, 5, 2])
    self.assertEqual(LCP_T, [1, 1, 3, 0, 2])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(
        [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 5])
    self.assertEqual(A_T, [1, 9, 2, 10, 3, 11, 4, 12, 5, 6, 7, 8])
    self.assertEqual(LCP_T, [3, 0, 2, 0, 1, 0, 0, 1, 0, 0, 0])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(
        [1, 2, 3, 4, 5, 6, 7, 8])
    self.assertEqual(A_T, [1, 2, 3, 4, 5, 6, 7, 8])
    self.assertEqual(LCP_T, [0, 0, 0, 0, 0, 0, 0])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree([2, 1, 3, 1, 3, 1])
    self.assertEqual(A_T, [6, 4, 2, 1, 5, 3])
    self.assertEqual(LCP_T, [1, 3, 0, 0, 2])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(
        [1, 1, 2, 2, 1, 3, 2, 3])
    self.assertEqual(A_T, [1, 2, 5, 4, 3, 7, 8, 6])
    self.assertEqual(LCP_T, [1, 1, 0, 1, 1, 0, 1])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(
        [1, 2, 3, 1, 1, 1, 2, 2, 3, 1, 1, 1, 1, 2, 1])
    self.assertEqual(A_T, [15, 10, 11, 4, 12, 5, 13, 6, 1, 14, 7, 8, 2, 9, 3])
    self.assertEqual(LCP_T, [1, 3, 4, 2, 3, 1, 2, 2, 0, 1, 1, 5, 0, 4])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(
        [1, 1, 1, 2, 3, 2, 1, 1, 1, 2, 4, 1, 1, 1, 2, 3, 2, 1, 1, 2, 3, 2, 1])
    self.assertEqual(A_T,
                     [23, 1, 12, 7, 18, 2, 13, 8, 19, 3, 14, 9, 22, 6, 17, 20,
                      4, 15, 10, 21,
                      5, 16, 11])
    self.assertEqual(LCP_T,
                     [1, 8, 4, 2, 6, 7, 3, 1, 5, 6, 2, 0, 2, 3, 1, 4, 5, 1, 0, 3, 4, 0])

    _, A_T, LCP_T = farach_suffix_tree.build_suffix_tree(
        [1, 1, 2, 2, 1, 3, 2, 1, 3, 2, 1, 1, 2, 3, 2, 2, 3])
    self.assertEqual(A_T,
                     [1, 11, 2, 12, 8, 5, 10, 7, 4, 3, 15, 16, 13, 17, 9, 6, 14])
    self.assertEqual(LCP_T, [3, 1, 2, 1, 4, 0, 2, 5, 1, 2, 1, 2, 0, 1, 3, 2])


if __name__ == '__main__':
  unittest.main()
