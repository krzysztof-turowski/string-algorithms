import unittest
import random

from string_indexing import lcp, suffix_array, wee_lcp

class TestWeeLCP(unittest.TestCase):
  def check_wee_lcp(self, text, delta):
    suf_array = suffix_array.naive(text, len(text))
    lcp_array = lcp.kasai(suf_array, text, len(text))
    bit_string = wee_lcp.compress_lcp_to_bit_string(lcp_array, suf_array)
    wee_lcp_2n = wee_lcp.CompressedLCP2n(bit_string, suf_array)
    wee_lcp_o_n = wee_lcp.CompressedLCPon(bit_string, text, suf_array, delta)
    for i in range(1, len(text)):
      self.assertEqual(lcp_array[i], wee_lcp_2n.lcp(i))
      self.assertEqual(lcp_array[i], wee_lcp_o_n.lcp(i))

  def unit_tests(self):
    self.check_wee_lcp("#AAAAA", 1)
    self.check_wee_lcp("#CACAACCAC", 1)
    self.check_wee_lcp("#banana", 1)
    self.check_wee_lcp('#mississippi', 0.3)
    self.check_wee_lcp('#abaabbaaabbbaaaabbbb', 5)

  def random_test(self):
    alphabet = ['A', 'B']
    size = 1000
    word = "#"
    while len(word) < size:
      word += alphabet[random.randint(0, 1)]
    self.check_wee_lcp(word, 0.5)

w = TestWeeLCP()
w.unit_tests()
for _ in range(5):
  w.random_test()
