import unittest

from benchar import benchar
from exact_string_matching import forward

class TestBenchar(unittest.TestCase):
    def test_same_benchar(self):
        test_benchar = benchar.benchar()
        t = test_benchar('#abrakababra')
        w = test_benchar('#brak')
        n = 11
        m = 4
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar.cmp_count, 12)

    def test_different_benchars(self):
        test_benchar_t = benchar.benchar()
        test_benchar_w = benchar.benchar()
        t = test_benchar_t('#abrakrdabra')
        w = test_benchar_w('#ra')
        n = 11
        m = 2
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar_t.cmp_count + test_benchar_w.cmp_count, 13)
        
    def test_benchar_str(self):
        test_benchar = benchar.benchar()
        t = test_benchar('#abrbkababra')
        w = '#br'
        n = 11
        m = 2
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar.cmp_count, 14)

    def test_str_benchar(self):
        test_benchar = benchar.benchar()
        t = '#bbrakababra'
        w = test_benchar('#brak')
        n = 11
        m = 4
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar.cmp_count, 13)
