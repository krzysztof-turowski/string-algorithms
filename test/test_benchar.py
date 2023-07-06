import unittest
import os

from exact_string_matching import forward
from benchar import benchar

if os.environ.get('CBENCHAR') is not None:
    from benchar.build import cbenchar

class TestBenchar(unittest.TestCase):
    run_cbenchar = unittest.skipUnless(
      os.environ.get('CBENCHAR', False), 'Skip test unless CBENCHAR variable specified')
    
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

    @run_cbenchar
    def test_same_cbenchar(self):
        test_benchar = cbenchar.benchar()
        t = test_benchar('#abrakababra')
        w = test_benchar('#brak')
        n = 11
        m = 4
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar.cmp_count, 12)

    @run_cbenchar
    def test_different_cbenchars(self):
        test_benchar_t = cbenchar.benchar()
        test_benchar_w = cbenchar.benchar()
        t = test_benchar_t('#abrakrdabra')
        w = test_benchar_w('#ra')
        n = 11
        m = 2
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar_t.cmp_count + test_benchar_w.cmp_count, 13)
    
    @run_cbenchar
    def test_cbenchar_str(self):
        test_benchar = cbenchar.benchar()
        t = test_benchar('#abrbkababra')
        w = '#br'
        n = 11
        m = 2
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar.cmp_count, 14)

    @run_cbenchar
    def test_str_cbenchar(self):
        test_benchar = cbenchar.benchar()
        t = '#bbrakababra'
        w = test_benchar('#brak')
        n = 11
        m = 4
        
        list(forward.brute_force(t, w, n, m))
        
        self.assertEqual(test_benchar.cmp_count, 13)
