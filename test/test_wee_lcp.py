import unittest
import random

from string_indexing import lcp, suffix_array, wee_lcp

class TestWeeLCP(unittest.TestCase):
    def check_wee_lcp(self, text, delta):
        SA = suffix_array.naive(text, len(text))
        LCP = lcp.kasai(SA, text, len(text))
        S = wee_lcp.compress_LCP_to_bit_string(LCP, SA)
        wee_lcp_2n = wee_lcp.compressed_LCP_2n(S, SA)
        wee_lcp_o_n = wee_lcp.compressed_LCP_o_n(S, text, SA, delta)
        for i in range(1, len(text)):
            self.assertEqual(LCP[i], wee_lcp_2n.lcp(i))
            self.assertEqual(LCP[i], wee_lcp_o_n.lcp(i))

    def unit_tests(self):
        self.check_wee_lcp("#AAAAA", 1)
        self.check_wee_lcp("#CACAACCAC", 1)
        self.check_wee_lcp("#banana", 1)
        self.check_wee_lcp('#mississippi', 0.3)
        self.check_wee_lcp('#abaabbaaabbbaaaabbbb', 5)
    
    def random_test(self):
        alphabet = ['A', 'B']
        size = 10000
        word = "#"
        for i in range(size):
            word += alphabet[random.randint(0, 1)]
        self.check_wee_lcp(word, 0.5)

w = TestWeeLCP()
w.unit_tests()
for i in range(5):
    w.random_test()
