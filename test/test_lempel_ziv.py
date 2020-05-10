import itertools
import os
import unittest

from compression import lempel_ziv
from generator import rand

class TestLempelZiv77(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_lempel_ziv_77(self, t, n, reference):
    self.assertEqual(lempel_ziv.lz77(t, n), reference)

  def check_recode_lempel_ziv_77(self, t, n):
    self.assertEqual(lempel_ziv.inverse_lz77(lempel_ziv.lz77(t, n)), t)

  def test_lempel_ziv_77(self):
    self.check_lempel_ziv_77(
        '#ababcbababaa', 12,
        [(0, 0, 'a'), (0, 0, 'b'), (2, 2, 'c'), (4, 3, 'a'), (2, 2, 'a')])
    self.check_lempel_ziv_77(
        '#aacaacabcabaaac', 15,
        [(0, 0, 'a'), (1, 1, 'c'), (3, 4, 'b'), (3, 3, 'a'), (1, 2, 'c')])

  def test_recode_lempel_ziv_77(self):
    self.check_recode_lempel_ziv_77('#ababcbababaa', 12)
    self.check_recode_lempel_ziv_77('#aacaacabcabaaac', 15)

  @run_large
  def test_random_recode_lempel_ziv_77(self):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      self.check_recode_lempel_ziv_77(t, n)

  @run_large
  def test_all_recode_lempel_ziv_77(self):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        self.check_recode_lempel_ziv_77(t, n)
