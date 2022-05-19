import os
import unittest

from compression import lempel_ziv_factorization
from generator import rand


class TestLempelZivFactorization(unittest.TestCase):
  run_large = unittest.skipUnless(
    os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_input(self, text, answer=None):
    n = len(text)
    text = '#' + text
    answer = answer or lempel_ziv_factorization.naive(text, n)

    alg0 = lempel_ziv_factorization.naive(text, n)
    alg1 = lempel_ziv_factorization.chrochemore_ille_smith(text, n)

    self.assertEqual(alg0, answer)
    self.assertEqual(alg1, answer)

  def test_lz_factorization_corners(self):
    self.check_input('', [-1])
    self.check_input('a', [-1, 1])
    self.check_input('aa', [-1, 1, 1])
    self.check_input('ab', [-1, 1, 1])
    self.check_input('aaaa', [-1, 1, 3])
    self.check_input('abab', [-1, 1, 1, 2])
    self.check_input('abbaabbbaaabab', [-1, 1, 1, 1, 1, 3, 3, 2, 2])
    self.check_input('ababcbababaa')
    self.check_input('eacacad')
    self.check_input('aacaacabcabaaac')
    self.check_input('abaab')
    self.check_input('aabbbbc')

  @run_large
  def test_lpf_random(self):
    T, n, A = 100, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)
      self.check_input(text)
