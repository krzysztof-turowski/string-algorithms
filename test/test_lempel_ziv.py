import itertools
import os
import unittest

from compression import lempel_ziv

class TestLempelZiv77(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_lempel_ziv_77(self, t, n, reference):
    self.assertEqual(lempel_ziv.lz77(t, n), reference)

  def test_lempel_ziv_77(self):
    self.check_lempel_ziv_77(
        '#ababcbababaa', 12,
        [(0, 0, 'a'), (0, 0, 'b'), (2, 2, 'c'), (4, 3, 'a'), (2, 2, 'a')])
    self.check_lempel_ziv_77(
        '#aacaacabcabaaac', 15,
        [(0, 0, 'a'), (1, 1, 'c'), (3, 4, 'b'), (3, 3, 'a'), (1, 2, 'c')])
